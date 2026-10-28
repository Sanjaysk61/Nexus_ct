
let currentRole = 'buyer';

document.addEventListener('DOMContentLoaded', () => {
    setupRoleSelector();
    setupChatForm();
    setupQuickPrompts();
    fetchPendingActions();
});

function setupRoleSelector() {
    const roleBtns = document.querySelectorAll('.role-btn');
    roleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            roleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentRole = btn.getAttribute('data-role');
            addAuditLog(`RBAC Role switched to '${currentRole.toUpperCase()}'`);
        });
    });
}

function setupQuickPrompts() {
    const chips = document.querySelectorAll('.prompt-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.getAttribute('data-prompt');
            document.getElementById('user-input').value = prompt;
            document.getElementById('chat-form').dispatchEvent(new Event('submit'));
        });
    });
}

function setupChatForm() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('user-input');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = input.value.trim();
        if (!query) return;

        appendMessage('user', query);
        input.value = '';

        const assistantMsgDiv = appendMessage('assistant', 'Analyzing procurement streams...');

        const startTime = performance.now();
        try {
            const res = await fetch('/api/v1/copilot/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    role: currentRole,
                    operator: 'User'
                })
            });

            const data = await res.json();
            const latency = Math.round(performance.now() - startTime);
            document.getElementById('header-latency').innerText = `LATENCY: ${latency}ms`;

            renderAssistantResponse(assistantMsgDiv, data);

            if (data.pending_action) {
                fetchPendingActions();
            }

            addAuditLog(`Query processed (${data.role}): "${query.substring(0, 30)}..."`);
        } catch (err) {
            assistantMsgDiv.querySelector('.msg-content').innerText = `Error: ${err.message}`;
        }
    });
}

function appendMessage(sender, text) {
    const chatViewport = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;

    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    msgDiv.innerHTML = `
        <div class="msg-header">
            <span class="sender-name">${sender === 'user' ? 'Operator' : 'NEXUS Copilot'}</span>
            <span class="msg-time">${now}</span>
        </div>
        <div class="msg-content">${formatMarkdown(text)}</div>
    `;

    chatViewport.appendChild(msgDiv);
    chatViewport.scrollTop = chatViewport.scrollHeight;
    return msgDiv;
}

function renderAssistantResponse(msgDiv, data) {
    const contentDiv = msgDiv.querySelector('.msg-content');
    let html = formatMarkdown(data.response_text);

    if (data.citations && data.citations.length > 0) {
        html += '<div style="margin-top: 10px;">';
        data.citations.forEach(c => {
            html += `<span class="citation-pill">📌 ${c.document_id} (${c.clause})</span> `;
        });
        html += '</div>';
    }

    contentDiv.innerHTML = html;
}

function formatMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/\n/g, '<br>')
        .replace(/### (.*?)(<br>|$)/g, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code style="background: #1e293b; padding: 2px 4px; border-radius: 3px;">$1</code>');
}

async function fetchPendingActions() {
    try {
        const res = await fetch('/api/v1/copilot/pending-actions');
        const data = await res.json();
        const list = document.getElementById('pending-actions-list');
        const badge = document.getElementById('pending-count-badge');

        const pending = data.pending_actions || [];
        badge.innerText = `${pending.length} Pending`;

        if (pending.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">✅</span>
                    <p>No actions pending operator sign-off.</p>
                    <span class="empty-sub">When the agent stages an administrative hold or dispute, it appears here for approval.</span>
                </div>
            `;
            return;
        }

        list.innerHTML = '';
        pending.forEach(action => {
            const card = document.createElement('div');
            card.className = 'action-card';
            card.innerHTML = `
                <div class="action-card-header">
                    <span>${action.action_type}</span>
                    <span>${action.impact_level} IMPACT</span>
                </div>
                <div class="action-card-body">
                    <p><strong>Target PO:</strong> ${action.purchase_order_id}</p>
                    <p>${action.recommended_action}</p>
                </div>
                <div class="action-card-buttons">
                    <button class="btn-approve" onclick="decideAction('${action.action_id}', 'APPROVED')">Approve Action</button>
                    <button class="btn-reject" onclick="decideAction('${action.action_id}', 'REJECTED')">Reject</button>
                </div>
            `;
            list.appendChild(card);
        });
    } catch (e) {
        console.error(e);
    }
}

async function decideAction(actionId, decision) {
    try {
        await fetch(`/api/v1/copilot/actions/${actionId}/decide`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                decision: decision,
                reviewer: `${currentRole.toUpperCase()}_OPERATOR`,
                comments: 'Decision logged via Cockpit UI'
            })
        });

        addAuditLog(`Action ${actionId} ${decision} by ${currentRole.toUpperCase()}`);
        fetchPendingActions();
    } catch (e) {
        alert(e.message);
    }
}

function addAuditLog(text) {
    const feed = document.getElementById('audit-feed');
    const item = document.createElement('div');
    item.className = 'audit-item';
    const time = new Date().toLocaleTimeString();
    item.innerHTML = `<span class="audit-time">${time}</span><span class="audit-text">${text}</span>`;
    feed.insertBefore(item, feed.firstChild);
}
