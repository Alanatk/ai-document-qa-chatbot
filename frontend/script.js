document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const fileList = document.getElementById('file-list');
    const processBtn = document.getElementById('process-btn');
    
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');
    
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');

    let uploadedFiles = new Map();
    let isProcessed = false;

    // File Upload Handlers
    browseBtn.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('click', (e) => {
        if (e.target !== browseBtn) fileInput.click();
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
        fileInput.value = ''; // Reset input to allow selecting same file again if removed
    });

    function handleFiles(files) {
        Array.from(files).forEach(file => {
            const ext = file.name.split('.').pop().toLowerCase();
            if (['pdf', 'txt', 'docx'].includes(ext)) {
                if (!uploadedFiles.has(file.name)) {
                    uploadedFiles.set(file.name, file);
                    renderFile(file);
                }
            } else {
                alert(`File type .${ext} is not supported. Please upload PDF, TXT, or DOCX.`);
            }
        });
        updateProcessButton();
    }

    function renderFile(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fa-solid fa-file-${getFileIcon(file.name)}"></i>
                <span class="file-name" title="${file.name}">${file.name}</span>
            </div>
            <button class="remove-btn" title="Remove file">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;

        fileItem.querySelector('.remove-btn').addEventListener('click', (e) => {
            e.stopPropagation(); // prevent clicking behind
            uploadedFiles.delete(file.name);
            fileItem.remove();
            updateProcessButton();
            if (uploadedFiles.size === 0) resetState();
        });

        fileList.appendChild(fileItem);
    }

    function getFileIcon(filename) {
        if (filename.endsWith('.pdf')) return 'pdf';
        if (filename.endsWith('.txt')) return 'lines';
        if (filename.endsWith('.docx')) return 'word';
        return 'alt';
    }

    function updateProcessButton() {
        processBtn.disabled = uploadedFiles.size === 0;
        if(uploadedFiles.size > 0 && !isProcessed) {
            processBtn.innerHTML = '<i class="fa-solid fa-microchip"></i> Process Documents';
            processBtn.classList.remove('success');
        }
    }

    function resetState() {
        isProcessed = false;
        chatInput.disabled = true;
        sendBtn.disabled = true;
        statusDot.className = 'dot offline';
        statusText.textContent = 'Awaiting Documents';
        processBtn.innerHTML = '<i class="fa-solid fa-microchip"></i> Process Documents';
        chatMessages.innerHTML = `
            <div class="message system-message">
                <div class="message-content">
                    <i class="fa-solid fa-info-circle"></i>
                    <p>👈 Please use the sidebar to upload & process documents first.</p>
                </div>
            </div>
        `;
    }

    // Process Documents Action
    processBtn.addEventListener('click', async () => {
        if (uploadedFiles.size === 0) return;

        // UI state update to processing
        processBtn.disabled = true;
        processBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        statusDot.className = 'dot processing';
        statusText.textContent = 'Processing...';

        // Simulate a backend API call to vectorize documents
        await new Promise(resolve => setTimeout(resolve, 2500));

        isProcessed = true;
        processBtn.innerHTML = '<i class="fa-solid fa-check"></i> Processed';
        processBtn.style.background = 'var(--success)';
        processBtn.style.boxShadow = '0 4px 16px rgba(16, 185, 129, 0.3)';
        
        statusDot.className = 'dot online';
        statusText.textContent = 'Ready';

        chatInput.disabled = false;
        sendBtn.disabled = true; // Still disabled if empty
        
        chatMessages.innerHTML = `
            <div class="message system-message" style="background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.2); color: #10b981;">
                <div class="message-content">
                    <i class="fa-solid fa-check-circle"></i>
                    <p>Successfully processed ${uploadedFiles.size} document(s). I'm ready to answer your questions!</p>
                </div>
            </div>
        `;
    });

    // Chat Functionality
    chatInput.addEventListener('input', () => {
        sendBtn.disabled = chatInput.value.trim() === '';
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text || !isProcessed) return;

        appendMessage('user', text);
        chatInput.value = '';
        sendBtn.disabled = true;

        const typingId = showTypingIndicator();

        // Simulate AI response (Mock representation of the RAG pipeline call)
        await new Promise(resolve => setTimeout(resolve, 1800));
        
        removeMessage(typingId);
        
        const mockResponse = `This is a beautiful custom frontend demonstrating the new UI capabilities! 
        
To fully wire this up to your python backend, you will need to replace the **Streamlit** \`app.py\` with a web API framework like **FastAPI** or **Flask**. The API will expose endpoints for uploading the documents and handling the chat messages, returning the data back to this frontend.
        
Let me know if you would like me to help build the API layer!`;
        
        appendMessage('assistant', mockResponse);
    });

    function appendMessage(role, content) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        if (role === 'assistant') {
            msgDiv.innerHTML = `
                <div class="avatar-wrapper">
                    <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                    <div class="message-content">${formatText(content)}</div>
                </div>
            `;
        } else {
            msgDiv.innerHTML = `<div class="message-content">${formatText(content)}</div>`;
        }
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = `message assistant`;
        msgDiv.id = id;
        msgDiv.innerHTML = `
            <div class="avatar-wrapper">
                <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="message-content">
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatText(text) {
        let formatted = text.replace(/\n\n/g, '</p><p>');
        formatted = `<p>${formatted}</p>`;
        // Basic bold markdown support for demo
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        return formatted;
    }
});
