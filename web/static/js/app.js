// Estado global
let library = {};
let selectedFiles = new Set();
let currentFilters = {
    category: 'all',
    resolution: 'all',
    search: ''
};
let collapsedCategories = new Set();
let collapsedResolutions = new Set();

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadLibrary();
    loadCollapsedState();
});

// Event Listeners
function initEventListeners() {
    // Toolbar
    document.getElementById('btn-refresh').addEventListener('click', handleRefresh);
    document.getElementById('btn-stats').addEventListener('click', handleShowStats);
    document.getElementById('search-input').addEventListener('input', handleSearch);
    
    // Filters
    document.getElementById('filter-category').addEventListener('change', handleFilterCategory);
    document.getElementById('filter-resolution').addEventListener('change', handleFilterResolution);
    
    // Bulk actions
    document.getElementById('bulk-category').addEventListener('change', handleBulkCategoryChange);
    document.getElementById('btn-bulk-move').addEventListener('click', handleBulkMove);
    document.getElementById('btn-bulk-delete').addEventListener('click', handleBulkDelete);
    document.getElementById('btn-deselect-all').addEventListener('click', handleDeselectAll);
    
    // Modal
    document.getElementById('modal-cancel').addEventListener('click', hideModal);
}

// Collapsed State Management
function loadCollapsedState() {
    const savedCategories = localStorage.getItem('collapsedCategories');
    const savedResolutions = localStorage.getItem('collapsedResolutions');
    
    if (savedCategories) {
        collapsedCategories = new Set(JSON.parse(savedCategories));
    }
    if (savedResolutions) {
        collapsedResolutions = new Set(JSON.parse(savedResolutions));
    }
}

function saveCollapsedState() {
    localStorage.setItem('collapsedCategories', JSON.stringify([...collapsedCategories]));
    localStorage.setItem('collapsedResolutions', JSON.stringify([...collapsedResolutions]));
}

function toggleCategory(category) {
    if (collapsedCategories.has(category)) {
        collapsedCategories.delete(category);
    } else {
        collapsedCategories.add(category);
    }
    saveCollapsedState();
    
    const section = document.querySelector(`.category-section[data-category="${category}"]`);
    if (section) {
        section.classList.toggle('collapsed');
    }
}

function toggleResolution(category, resolution) {
    const key = `${category}-${resolution}`;
    if (collapsedResolutions.has(key)) {
        collapsedResolutions.delete(key);
    } else {
        collapsedResolutions.add(key);
    }
    saveCollapsedState();
    
    const group = document.querySelector(`.resolution-group[data-resolution="${key}"]`);
    if (group) {
        group.classList.toggle('collapsed');
    }
}

// API Calls
async function loadLibrary() {
    showLoading(true);
    try {
        const response = await fetch('/api/library');
        const data = await response.json();
        
        if (data.success) {
            library = data.library;
            renderLibrary();
        } else {
            showToast('Error al cargar biblioteca', 'error');
        }
    } catch (error) {
        console.error('Error loading library:', error);
        showToast('Error de conexión', 'error');
    } finally {
        showLoading(false);
    }
}

async function moveFile(hash, toCategory, toResolution) {
    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                hash,
                to_category: toCategory,
                to_resolution: toResolution
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error moving file:', error);
        return { success: false, message: 'Error de conexión' };
    }
}

async function deleteFiles(hashes) {
    try {
        const response = await fetch('/api/delete', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hashes })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error deleting files:', error);
        return { success: false, message: 'Error de conexión' };
    }
}

async function moveBulkFiles(hashes, toCategory, toResolution) {
    try {
        const response = await fetch('/api/move-bulk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                hashes,
                to_category: toCategory,
                to_resolution: toResolution
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error moving files:', error);
        return { success: false, message: 'Error de conexión' };
    }
}

async function refreshLibrary() {
    try {
        const response = await fetch('/api/refresh', {
            method: 'POST'
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error refreshing library:', error);
        return { success: false, message: 'Error de conexión' };
    }
}

// Render Functions
function renderLibrary() {
    const container = document.getElementById('library-container');
    container.innerHTML = '';
    
    const categories = ['movies', 'series', 'music', 'others'];
    const categoryIcons = {
        movies: '🎬',
        series: '📺',
        music: '🎵',
        others: '📁'
    };
    
    let hasVisibleFiles = false;
    
    categories.forEach(category => {
        const files = library[category] || [];
        const filteredFiles = filterFiles(files, category);
        
        if (filteredFiles.length === 0) return;
        
        hasVisibleFiles = true;
        
        const section = document.createElement('div');
        section.className = 'category-section';
        section.dataset.category = category;
        
        if (collapsedCategories.has(category)) {
            section.classList.add('collapsed');
        }
        
        // Header
        const header = document.createElement('div');
        header.className = 'category-header';
        header.innerHTML = `
            <div class="category-header-left">
                <span class="collapse-icon">▼</span>
                <div class="category-title">
                    <span class="icon">${categoryIcons[category]}</span>
                    ${category.charAt(0).toUpperCase() + category.slice(1)}
                    <span class="category-count">${filteredFiles.length}</span>
                </div>
            </div>
            <div class="select-all-container" onclick="event.stopPropagation()">
                <input type="checkbox" id="select-all-${category}" class="file-checkbox">
                <label for="select-all-${category}">Todo</label>
            </div>
        `;
        
        // Toggle collapse on header click
        header.addEventListener('click', (e) => {
            if (!e.target.closest('.select-all-container')) {
                toggleCategory(category);
            }
        });
        
        section.appendChild(header);
        
        // Content wrapper
        const content = document.createElement('div');
        content.className = 'category-content';
        
        // Select all checkbox
        const selectAllCheckbox = header.querySelector(`#select-all-${category}`);
        selectAllCheckbox.addEventListener('change', (e) => {
            handleSelectAll(category, e.target.checked);
        });
        
        // Group by resolution for movies
        if (category === 'movies') {
            const grouped = groupByResolution(filteredFiles);
            Object.keys(grouped).sort().reverse().forEach(resolution => {
                const resolutionKey = `${category}-${resolution}`;
                const resolutionGroup = document.createElement('div');
                resolutionGroup.className = 'resolution-group';
                resolutionGroup.dataset.resolution = resolutionKey;
                
                if (collapsedResolutions.has(resolutionKey)) {
                    resolutionGroup.classList.add('collapsed');
                }
                
                const resolutionHeader = document.createElement('div');
                resolutionHeader.className = 'resolution-header';
                resolutionHeader.innerHTML = `
                    <span>${resolution}p (${grouped[resolution].length})</span>
                    <span class="resolution-collapse-icon">▼</span>
                `;
                resolutionHeader.addEventListener('click', () => {
                    toggleResolution(category, resolution);
                });
                resolutionGroup.appendChild(resolutionHeader);
                
                const resolutionContent = document.createElement('div');
                resolutionContent.className = 'resolution-content';
                
                const fileList = document.createElement('div');
                fileList.className = 'file-list';
                grouped[resolution].forEach(file => {
                    fileList.appendChild(createFileItem(file, category));
                });
                resolutionContent.appendChild(fileList);
                resolutionGroup.appendChild(resolutionContent);
                
                content.appendChild(resolutionGroup);
            });
        } else {
            const fileList = document.createElement('div');
            fileList.className = 'file-list';
            filteredFiles.forEach(file => {
                fileList.appendChild(createFileItem(file, category));
            });
            content.appendChild(fileList);
        }
        
        section.appendChild(content);
        container.appendChild(section);
    });
    
    if (!hasVisibleFiles) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📭</div>
                <h3>No se encontraron archivos</h3>
                <p>Intenta cambiar los filtros o realizar un refresh</p>
            </div>
        `;
    }
}

function createFileItem(file, category) {
    const item = document.createElement('div');
    item.className = 'file-item';
    item.dataset.hash = file.hash;
    
    if (selectedFiles.has(file.hash)) {
        item.classList.add('selected');
    }
    
    const yearText = file.year ? ` (${file.year})` : '';
    
    // Badges
    let badges = [];
    if (file.manual_override) {
        badges.push('<span class="file-badge badge-manual">🔒</span>');
    }
    
    // Calcular tiempo restante hasta expiración
    let expiryInfo = '';
    if (file.expires_at) {
        const now = Date.now();
        const expiresDate = new Date(file.expires_at);
        const timeLeft = expiresDate - now;
        const daysLeft = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hoursLeft = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        
        if (daysLeft < 0) {
            badges.push('<span class="file-badge badge-expired">⚠️</span>');
            expiryInfo = '⚠️ Expirado';
        } else if (daysLeft === 0) {
            badges.push('<span class="file-badge badge-expiring-soon">⏰</span>');
            expiryInfo = `⏰ ${hoursLeft}h`;
        } else if (daysLeft < 3) {
            badges.push('<span class="file-badge badge-expiring-soon">⏰</span>');
            expiryInfo = `⏰ ${daysLeft}d`;
        } else if (daysLeft < 7) {
            expiryInfo = `⏳ ${daysLeft}d`;
        } else {
            expiryInfo = `✓ ${daysLeft}d`;
        }
    }
    
    item.innerHTML = `
        <div class="file-header">
            <input type="checkbox" class="file-checkbox" data-hash="${file.hash}" ${selectedFiles.has(file.hash) ? 'checked' : ''}>
            <div class="file-title">${file.title}${yearText}</div>
            <div class="file-badges">${badges.join('')}</div>
        </div>
        <div class="file-info">
            <span>📁 ${file.category}</span>
            <span>📺 ${file.resolution}p</span>
            <span>💿 ${file.format}</span>
            ${expiryInfo ? `<span>${expiryInfo}</span>` : ''}
        </div>
        <div class="file-actions">
            <select class="action-category" data-hash="${file.hash}">
                <option value="">Cat...</option>
                <option value="movies" ${category === 'movies' ? 'selected' : ''}>Movies</option>
                <option value="series" ${category === 'series' ? 'selected' : ''}>Series</option>
                <option value="music" ${category === 'music' ? 'selected' : ''}>Music</option>
                <option value="others" ${category === 'others' ? 'selected' : ''}>Others</option>
            </select>
            <select class="action-resolution" data-hash="${file.hash}" ${category !== 'movies' ? 'style="display: none;"' : ''}>
                <option value="">Res...</option>
                <option value="2160" ${file.resolution === '2160' ? 'selected' : ''}>2160p</option>
                <option value="1080" ${file.resolution === '1080' ? 'selected' : ''}>1080p</option>
                <option value="720" ${file.resolution === '720' ? 'selected' : ''}>720p</option>
                <option value="480" ${file.resolution === '480' ? 'selected' : ''}>480p</option>
                <option value="unknown" ${file.resolution === 'unknown' ? 'selected' : ''}>Unknown</option>
            </select>
            <button class="btn btn-primary btn-small btn-apply" data-hash="${file.hash}">
                ✓
            </button>
            <button class="btn btn-danger btn-small btn-delete" data-hash="${file.hash}">
                🗑️
            </button>
        </div>
    `;
    
    // Event listeners
    const checkbox = item.querySelector('.file-checkbox');
    checkbox.addEventListener('change', (e) => {
        handleFileSelect(file.hash, e.target.checked);
    });
    
    const categorySelect = item.querySelector('.action-category');
    const resolutionSelect = item.querySelector('.action-resolution');
    
    categorySelect.addEventListener('change', (e) => {
        if (e.target.value === 'movies') {
            resolutionSelect.style.display = 'block';
        } else {
            resolutionSelect.style.display = 'none';
        }
    });
    
    const applyBtn = item.querySelector('.btn-apply');
    applyBtn.addEventListener('click', () => {
        handleApplyMove(file.hash, categorySelect.value, resolutionSelect.value);
    });
    
    const deleteBtn = item.querySelector('.btn-delete');
    deleteBtn.addEventListener('click', () => {
        handleDeleteFile(file.hash, file.title);
    });
    
    return item;
}

// Filter Functions
function filterFiles(files, category) {
    return files.filter(file => {
        // Category filter
        if (currentFilters.category !== 'all' && category !== currentFilters.category) {
            return false;
        }
        
        // Resolution filter
        if (currentFilters.resolution !== 'all' && file.resolution !== currentFilters.resolution) {
            return false;
        }
        
        // Search filter
        if (currentFilters.search) {
            const searchLower = currentFilters.search.toLowerCase();
            const titleMatch = file.title.toLowerCase().includes(searchLower);
            const yearMatch = file.year && file.year.toString().includes(searchLower);
            return titleMatch || yearMatch;
        }
        
        return true;
    });
}

function groupByResolution(files) {
    const grouped = {};
    files.forEach(file => {
        const res = file.resolution || 'unknown';
        if (!grouped[res]) {
            grouped[res] = [];
        }
        grouped[res].push(file);
    });
    return grouped;
}

// Event Handlers
function handleSearch(e) {
    currentFilters.search = e.target.value;
    renderLibrary();
}

function handleFilterCategory(e) {
    currentFilters.category = e.target.value;
    renderLibrary();
}

function handleFilterResolution(e) {
    currentFilters.resolution = e.target.value;
    renderLibrary();
}

function handleFileSelect(hash, checked) {
    if (checked) {
        selectedFiles.add(hash);
    } else {
        selectedFiles.delete(hash);
    }
    updateBulkActions();
    updateFileItemSelection(hash, checked);
}

function handleSelectAll(category, checked) {
    const files = library[category] || [];
    const filteredFiles = filterFiles(files, category);
    
    filteredFiles.forEach(file => {
        if (checked) {
            selectedFiles.add(file.hash);
        } else {
            selectedFiles.delete(file.hash);
        }
    });
    
    updateBulkActions();
    renderLibrary();
}

function handleDeselectAll() {
    selectedFiles.clear();
    updateBulkActions();
    renderLibrary();
}

function handleBulkCategoryChange(e) {
    const category = e.target.value;
    const resolutionSelect = document.getElementById('bulk-resolution');
    const moveBtn = document.getElementById('btn-bulk-move');
    
    if (category === 'movies') {
        resolutionSelect.style.display = 'block';
    } else {
        resolutionSelect.style.display = 'none';
    }
    
    moveBtn.disabled = !category;
}

async function handleBulkMove() {
    const category = document.getElementById('bulk-category').value;
    const resolution = document.getElementById('bulk-resolution').value;
    
    if (!category) {
        showToast('Selecciona una categoría', 'error');
        return;
    }
    
    const hashes = Array.from(selectedFiles);
    
    showModal(
        'Confirmar movimiento masivo',
        `¿Mover ${hashes.length} archivo(s) a ${category}${resolution ? '/' + resolution : ''}?`,
        async () => {
            showLoading(true);
            const result = await moveBulkFiles(hashes, category, resolution);
            showLoading(false);
            
            if (result.success) {
                showToast(result.message, 'success');
                selectedFiles.clear();
                await loadLibrary();
            } else {
                showToast(result.message, 'error');
            }
        }
    );
}

async function handleBulkDelete() {
    const hashes = Array.from(selectedFiles);
    
    showModal(
        'Confirmar eliminación masiva',
        `¿Eliminar ${hashes.length} archivo(s)? Esta acción no se puede deshacer.`,
        async () => {
            showLoading(true);
            const result = await deleteFiles(hashes);
            showLoading(false);
            
            if (result.success) {
                showToast(result.message, 'success');
                selectedFiles.clear();
                await loadLibrary();
            } else {
                showToast(result.message, 'error');
            }
        }
    );
}

async function handleApplyMove(hash, category, resolution) {
    if (!category) {
        showToast('Selecciona una categoría', 'error');
        return;
    }
    
    showLoading(true);
    const result = await moveFile(hash, category, resolution);
    showLoading(false);
    
    if (result.success) {
        showToast(result.message, 'success');
        await loadLibrary();
    } else {
        showToast(result.message, 'error');
    }
}

async function handleDeleteFile(hash, title) {
    showModal(
        'Confirmar eliminación',
        `¿Eliminar "${title}"? Esta acción no se puede deshacer.`,
        async () => {
            showLoading(true);
            const result = await deleteFiles([hash]);
            showLoading(false);
            
            if (result.success) {
                showToast('Archivo eliminado exitosamente', 'success');
                await loadLibrary();
            } else {
                showToast(result.message, 'error');
            }
        }
    );
}

async function handleRefresh() {
    showLoading(true);
    showToast('Iniciando refresh...', 'info');
    
    const result = await refreshLibrary();
    
    if (result.success) {
        showToast('Refresh completado', 'success');
        await loadLibrary();
    } else {
        showLoading(false);
        showToast(result.message, 'error');
    }
}

async function handleShowStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            const message = `
                Total: ${stats.total_files} archivos
                
                Por categoría:
                • Movies: ${stats.by_category.movies || 0}
                • Series: ${stats.by_category.series || 0}
                • Music: ${stats.by_category.music || 0}
                • Others: ${stats.by_category.others || 0}
                
                Resoluciones (Movies):
                ${Object.entries(stats.by_resolution).map(([res, count]) => `• ${res}p: ${count}`).join('\n')}
                
                Manual overrides: ${stats.manual_overrides}
            `;
            
            showModal('Estadísticas de la Biblioteca', message, null);
        }
    } catch (error) {
        showToast('Error al obtener estadísticas', 'error');
    }
}

// UI Helper Functions
function updateBulkActions() {
    const bulkActions = document.getElementById('bulk-actions');
    const selectedCount = document.getElementById('selected-count');
    
    selectedCount.textContent = selectedFiles.size;
    
    if (selectedFiles.size > 0) {
        bulkActions.style.display = 'flex';
    } else {
        bulkActions.style.display = 'none';
    }
}

function updateFileItemSelection(hash, checked) {
    const item = document.querySelector(`.file-item[data-hash="${hash}"]`);
    if (item) {
        if (checked) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    }
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'block' : 'none';
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function showModal(title, message, onConfirm) {
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const confirmBtn = document.getElementById('modal-confirm');
    
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    modal.style.display = 'flex';
    
    // Remove old listeners
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    
    if (onConfirm) {
        newConfirmBtn.addEventListener('click', () => {
            hideModal();
            onConfirm();
        });
    } else {
        newConfirmBtn.style.display = 'none';
    }
}

function hideModal() {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
    document.getElementById('modal-confirm').style.display = 'block';
}
