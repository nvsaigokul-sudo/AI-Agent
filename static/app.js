// static/app.js

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const chatFeed = document.getElementById("chat-feed");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const clearBtn = document.getElementById("clear-btn");
    const taskList = document.getElementById("task-list");
    const taskCountBadge = document.getElementById("task-count");
    const scheduleTimeline = document.getElementById("schedule-timeline");
    const themeToggleBtn = document.getElementById("theme-toggle");
    const toast = document.getElementById("toast");

    // State Variables
    let isSubmitting = false;

    // 1. UTILITY FUNCTIONS
    // Show Toast Notifications
    function showToast(message, type = "success") {
        toast.textContent = message;
        toast.className = `toast ${type}`;
        setTimeout(() => toast.classList.remove("hidden"), 50);
        
        // Hide after 4 seconds
        setTimeout(() => {
            toast.classList.add("hidden");
        }, 4000);
    }

    // Toggle Themes (Dark / Light)
    themeToggleBtn.addEventListener("click", () => {
        const currentTheme = document.body.getAttribute("data-theme");
        if (currentTheme === "light") {
            document.body.removeAttribute("data-theme");
            themeToggleBtn.innerHTML = `
                <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
                </svg>
            `;
            showToast("Switched to dark theme");
        } else {
            document.body.setAttribute("data-theme", "light");
            themeToggleBtn.innerHTML = `
                <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="5"/>
                    <line x1="12" y1="1" x2="12" y2="3"/>
                    <line x1="12" y1="21" x2="12" y2="23"/>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                    <line x1="1" y1="12" x2="3" y2="12"/>
                    <line x1="21" y1="12" x2="23" y2="12"/>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                </svg>
            `;
            showToast("Switched to light theme");
        }
    });

    // Handle suggestion chips
    document.querySelectorAll(".suggestion-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            chatInput.value = chip.textContent;
            chatInput.focus();
        });
    });

    // Auto-scroll chat feed
    function scrollToBottom() {
        chatFeed.scrollTop = chatFeed.scrollHeight;
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Format schedule text output nicely if it contains "=== Study Planner Schedule ==="
    function formatMarkdownText(text) {
        if (text.includes("=== Study Planner Schedule ===")) {
            // Split tasks
            const blocks = text.split(/\d+\.\s+Task:/);
            let html = `<h3>Generated Plan</h3>`;
            
            blocks.forEach((block, idx) => {
                if (idx === 0) return; // Header block
                
                const lines = block.split('\n');
                let name = "";
                let due = "";
                let period = "";
                
                lines.forEach(line => {
                    if (line.includes("Due Date:")) due = line.replace("Due Date:", "").trim();
                    else if (line.includes("Study Period:")) period = line.replace("Study Period:", "").trim();
                    else if (line.trim()) name = line.trim();
                });
                
                if (name) {
                    html += `
                        <div style="background: rgba(255,255,255,0.015); border: 1px solid var(--border-color); padding: 10px; border-radius: 8px; margin-top: 8px;">
                            <strong>${escapeHtml(name)}</strong>
                            <div style="font-size: 12px; color: var(--color-text-muted); margin-top: 4px;">
                                📅 Due: ${escapeHtml(due)} <br/>
                                ⏱️ Study Slot: ${escapeHtml(period)}
                            </div>
                        </div>
                    `;
                }
            });
            return html;
        }
        
        // Simple replacements
        let formatted = escapeHtml(text)
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code class="inline-code">$1</code>')
            .replace(/\n/g, '<br/>');
            
        return formatted;
    }

    // 2. DATA RENDERING & API CALLS
    // Fetch registered tasks from backend
    async function fetchTasks() {
        try {
            const response = await fetch("/api/tasks");
            const tasks = await response.json();
            renderTaskList(tasks);
        } catch (error) {
            console.error("Error fetching tasks:", error);
        }
    }

    // Render registered task list panels
    function renderTaskList(tasks) {
        taskCountBadge.textContent = `${tasks.length} Task${tasks.length === 1 ? "" : "s"}`;
        
        if (tasks.length === 0) {
            taskList.innerHTML = `
                <div class="empty-state">
                    <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                        <line x1="16" y1="2" x2="16" y2="6"/>
                        <line x1="8" y1="2" x2="8" y2="6"/>
                        <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    <p>No tasks added in this session.</p>
                </div>
            `;
            return;
        }

        taskList.innerHTML = tasks.map(task => `
            <div class="task-item">
                <div class="task-details">
                    <span class="task-title">${escapeHtml(task.name)}</span>
                    <span class="task-due">
                        <svg class="calendar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
                        </svg>
                        Due: ${escapeHtml(task.due)}
                    </span>
                </div>
            </div>
        `).join("");
    }

    // Render generated timeline in side panel
    function renderScheduleTimeline(agentResponseText) {
        if (!agentResponseText.includes("=== Study Planner Schedule ===")) {
            return;
        }

        const blocks = agentResponseText.split(/\d+\.\s+Task:/);
        const timelineItems = [];

        blocks.forEach((block, idx) => {
            if (idx === 0) return; // Ignore prefix headers
            
            const lines = block.split('\n');
            let name = "";
            let due = "";
            let period = "";
            
            lines.forEach(line => {
                if (line.includes("Due Date:")) due = line.replace("Due Date:", "").trim();
                else if (line.includes("Study Period:")) period = line.replace("Study Period:", "").trim();
                else if (line.trim()) name = line.trim();
            });

            if (name) {
                timelineItems.push({ name, due, period });
            }
        });

        if (timelineItems.length === 0) return;

        scheduleTimeline.innerHTML = `
            <div class="timeline-list">
                ${timelineItems.map(item => `
                    <div class="timeline-item">
                        <div class="timeline-marker"></div>
                        <div class="timeline-card">
                            <div class="timeline-task-name">${escapeHtml(item.name)}</div>
                            <div class="timeline-meta">
                                <span class="timeline-meta-label">Deadline:</span>
                                <span>${escapeHtml(item.due)}</span>
                                <span class="timeline-meta-label">Study Slot:</span>
                                <span>${escapeHtml(item.period)}</span>
                            </div>
                        </div>
                    </div>
                `).join("")}
            </div>
        `;
    }

    // 3. AGENT STEP LOGS RENDERING (PLAN-ACT EXPLICIT LOOP)
    function createThinkingBlockHTML(step) {
        const detailsText = step.details.join('\n');
        const phaseClass = `phase-${step.phase.toLowerCase()}`;
        
        return `
            <div class="thinking-block ${phaseClass}">
                <div class="thinking-header" onclick="this.parentElement.classList.toggle('open')">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="step-badge">${escapeHtml(step.phase)}</span>
                        <span>Step ${step.number}: ${escapeHtml(step.message)}</span>
                    </div>
                    <svg class="toggle-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                </div>
                <div class="thinking-content">${escapeHtml(detailsText)}</div>
            </div>
        `;
    }

    // 4. MESSAGE INGESTION & SUBMISSION
    async function sendMessage(messageText) {
        if (isSubmitting) return;
        isSubmitting = true;

        // Disable UI controls
        chatInput.disabled = true;
        sendBtn.disabled = true;

        // Render user bubble
        const userBubble = document.createElement("div");
        userBubble.className = "chat-bubble user";
        userBubble.textContent = messageText;
        chatFeed.appendChild(userBubble);
        scrollToBottom();

        // Render agent placeholder thinking bubble
        const agentBubble = document.createElement("div");
        agentBubble.className = "chat-bubble agent thinking-indicator-container";
        agentBubble.innerHTML = `
            <div style="display:flex; align-items:center; gap:8px; color:var(--color-text-muted);">
                <div class="spinner" style="width:16px; height:16px; border:2px solid var(--border-color); border-top-color:var(--primary); border-radius:50%; animation:spin 0.8s linear infinite;"></div>
                <span>Agent is analyzing...</span>
            </div>
        `;
        chatFeed.appendChild(agentBubble);
        scrollToBottom();

        // CSS inline style for spinner animation if not present
        if (!document.getElementById("spinner-keyframe")) {
            const style = document.createElement('style');
            style.id = "spinner-keyframe";
            style.innerHTML = "@keyframes spin { to { transform: rotate(360deg); } }";
            document.head.appendChild(style);
        }

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) {
                throw new Error("Failed to reach agent server.");
            }

            const data = await response.json();
            
            // Remove agent loader
            agentBubble.innerHTML = "";
            agentBubble.classList.remove("thinking-indicator-container");

            // Render execution logs if they exist
            if (data.steps && data.steps.length > 0) {
                const logsContainer = document.createElement("div");
                logsContainer.className = "agent-execution-steps";
                logsContainer.innerHTML = data.steps.map(step => createThinkingBlockHTML(step)).join("");
                agentBubble.appendChild(logsContainer);
            }

            // Render final textual answer
            const textResponseEl = document.createElement("div");
            textResponseEl.className = "agent-response-text";
            textResponseEl.innerHTML = formatMarkdownText(data.response);
            agentBubble.appendChild(textResponseEl);

            // Re-render task visualizers
            renderTaskList(data.tasks);
            renderScheduleTimeline(data.response);
            
            // Success alert if schedule generated or tasks added
            if (messageText.toLowerCase().includes("schedule") || messageText.toLowerCase().includes("plan")) {
                if (data.response.includes("=== Study Planner Schedule ===")) {
                    showToast("Study schedule generated successfully!", "success");
                }
            } else {
                showToast("Task registered in session storage.", "success");
            }

        } catch (error) {
            agentBubble.innerHTML = `<p style="color:var(--danger)">⚠️ Error: ${escapeHtml(error.message)}</p>`;
            showToast("Failed to fetch response.", "error");
        } finally {
            isSubmitting = false;
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.value = "";
            chatInput.focus();
            scrollToBottom();
        }
    }

    // 5. CHAT FORM SUBMIT EVENT
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (text) {
            sendMessage(text);
        }
    });

    // 6. CLEAR MEMORY EVENT
    clearBtn.addEventListener("click", async () => {
        if (confirm("Are you sure you want to clear the registered task list and reset the conversation history?")) {
            try {
                const response = await fetch("/api/clear", { method: "POST" });
                const result = await response.json();
                
                // Clear UI timeline & task list
                renderTaskList([]);
                scheduleTimeline.innerHTML = `
                    <div class="empty-state">
                        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        <p>Ask the agent to "build schedule" to compile study periods.</p>
                    </div>
                `;
                
                // Clear chat feed except system welcome
                chatFeed.innerHTML = `
                    <div class="chat-bubble system-message">
                        <p>👋 Hello! I am your <strong>Study Planner Agent</strong>.</p>
                        <p>I maintain structured session memory and have tools to record your deadlines and build a chronological, optimized study schedule.</p>
                        <div class="suggestions">
                            <button class="suggestion-chip">Add Java Exam on September 5</button>
                            <button class="suggestion-chip">Add DBMS Assignment on September 2</button>
                            <button class="suggestion-chip">Build my study schedule</button>
                        </div>
                    </div>
                `;

                // Re-bind click events for dynamic welcome screen suggestion chips
                document.querySelectorAll(".suggestion-chip").forEach(chip => {
                    chip.addEventListener("click", () => {
                        chatInput.value = chip.textContent;
                        chatInput.focus();
                    });
                });
                
                showToast("Memory successfully cleared.");
            } catch (error) {
                showToast("Failed to clear memory.", "error");
            }
        }
    });

    // 7. INITIAL WORKSPACE LOADING
    async function checkAgentStatus() {
        try {
            const response = await fetch("/api/status");
            const data = await response.json();
            if (!data.ready) {
                // Render warning bubble in the feed
                const warningBubble = document.createElement("div");
                warningBubble.className = "chat-bubble system-message warning-banner";
                warningBubble.style.borderColor = "var(--danger)";
                warningBubble.style.borderWidth = "1px";
                warningBubble.style.borderStyle = "solid";
                warningBubble.style.background = "rgba(239, 68, 68, 0.08)";
                warningBubble.innerHTML = `
                    <p style="color: var(--danger); font-weight: 700; margin-bottom: 6px;">⚠️ Gemini API Key Missing</p>
                    <p style="font-size: 13px; color: var(--color-text-muted); margin-bottom: 10px;">${escapeHtml(data.message)}</p>
                    <div style="background: rgba(0,0,0,0.15); padding: 10px; border-radius: 8px; font-family: var(--font-mono); font-size: 11px; text-align: left; line-height: 1.5; color: var(--color-text-main);">
                        Create a file named <strong>.env</strong> in the project folder with:<br/>
                        <code style="color: var(--primary); font-weight: 600;">GEMINI_API_KEY=your_actual_api_key</code>
                    </div>
                `;
                chatFeed.appendChild(warningBubble);
                scrollToBottom();
            }
        } catch (error) {
            console.error("Error checking status:", error);
        }
    }

    checkAgentStatus();
    fetchTasks();
});
