// networking.js
export const appState = {
    backgroundColor: '#f0f0f0',
    links: []
};

export function loadNetworkingTab(containerId = 'main-content') {
    const mainContent = document.getElementById(containerId);
    if (!mainContent) {
        console.error(`Container with id ${containerId} not found`);
        return;
    }
    
    mainContent.innerHTML = `
        <div class="preview-container">
            <h3 class="section-title">Your Social Links</h3>
            
            <!-- Phone mockup -->
            <div class="phone-mockup" id="phone-preview">
                <div class="preview-content">
                    <div id="links-container" class="links-list"></div>
                    <div class="powered-by">
                        <p>Powered by NextLink</p>
                    </div>
                </div>
            </div>

            <!-- Controls -->
            <div class="controls">
                <button id="add-link-btn" class="add-button">
                    + Add New Link
                </button>
            </div>
        </div>

        <!-- Modal -->
        <div id="link-modal" class="modal hidden">
            <div class="modal-content">
                <h4>Add New Link</h4>
                <input type="text" id="link-title" placeholder="Link Title">
                <input type="url" id="link-url" placeholder="https://...">
                <div class="button-group">
                    <button id="save-link" class="save-btn">Save</button>
                    <button id="cancel-link" class="cancel-btn">Cancel</button>
                </div>
            </div>
        </div>
    `;

    // Apply stored background color
    const phonePreview = document.getElementById('phone-preview');
    if (phonePreview) {
        phonePreview.style.backgroundColor = appState.backgroundColor;
    }

    setupEventListeners();
    renderLinks();
}

function setupEventListeners() {
    document.getElementById('add-link-btn')?.addEventListener('click', () => {
        document.getElementById('link-modal')?.classList.remove('hidden');
    });

    document.getElementById('save-link')?.addEventListener('click', saveNewLink);

    document.getElementById('cancel-link')?.addEventListener('click', () => {
        document.getElementById('link-modal')?.classList.add('hidden');
        clearLinkForm();
    });
}

function saveNewLink() {
    const titleInput = document.getElementById('link-title');
    const urlInput = document.getElementById('link-url');

    if (!titleInput || !urlInput) return;

    const title = titleInput.value.trim();
    const url = urlInput.value.trim();

    if (!title || !url) {
        alert('Please fill in both title and URL');
        return;
    }

    appState.links.push({ title, url });
    renderLinks();
    clearLinkForm();
    document.getElementById('link-modal')?.classList.add('hidden');
}

function clearLinkForm() {
    const titleInput = document.getElementById('link-title');
    const urlInput = document.getElementById('link-url');
    
    if (titleInput) titleInput.value = '';
    if (urlInput) urlInput.value = '';
}

function renderLinks() {
    const container = document.getElementById('links-container');
    if (!container) return;

    container.innerHTML = appState.links.map(link => `
        <div class="link-item">
            <div class="link-content">
                <span class="material-icons">link</span>
                <div class="link-details">
                    <h4>${link.title}</h4>
                    <a href="${link.url}" target="_blank">${link.url}</a>
                </div>
            </div>
        </div>
    `).join('');
}

export function updateBackgroundColor(color) {
    appState.backgroundColor = color;
    const phonePreview = document.getElementById('phone-preview');
    if (phonePreview) {
        phonePreview.style.backgroundColor = color;
    }
}