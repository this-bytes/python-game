/**
 * Entity Editor Modal System
 * 
 * Provides advanced modal-based editing for game entities with:
 * - Visual form editors with validation
 * - JSON editor with syntax highlighting
 * - Real-time preview
 * - Duplicate and template features
 */

class EntityEditorModal {
    constructor(controlPanel) {
        this.controlPanel = controlPanel;
        this.currentEntity = null;
        this.currentEntityType = null;
        this.currentIndex = null;
        this.mode = 'edit'; // 'edit', 'create', 'duplicate'
        this.schema = null;
        this.schemas = {};
    }
    
    async loadSchema(entityType) {
        /**
         * Load schema for entity type from backend.
         */
        if (this.schemas[entityType]) {
            return this.schemas[entityType];
        }
        
        try {
            const response = await fetch(`${API_BASE}/schemas/${entityType}`);
            const data = await response.json();
            
            if (data.success) {
                this.schemas[entityType] = data.data;
                return data.data;
            }
        } catch (error) {
            console.warn(`Could not load schema for ${entityType}:`, error);
        }
        
        return null;
    }
    
    generateTemplateFromSchema(schema) {
        /**
         * Generate a template entity from schema definition.
         */
        if (!schema || !schema.schema) {
            return null;
        }
        
        const template = {};
        const schemaProps = schema.schema.properties;
        
        // Find the array property that contains entity items
        for (const propName in schemaProps) {
            const prop = schemaProps[propName];
            if (prop.type === 'array' && prop.items && prop.items.properties) {
                const itemProps = prop.items.properties;
                
                // Generate template with default values from schema
                for (const fieldName in itemProps) {
                    const field = itemProps[fieldName];
                    
                    if (field.default !== undefined) {
                        template[fieldName] = field.default;
                    } else if (field.type === 'string') {
                        if (fieldName === 'id') {
                            template[fieldName] = 'new_entity_id';
                        } else {
                            template[fieldName] = field.enum ? field.enum[0] : '';
                        }
                    } else if (field.type === 'number' || field.type === 'integer') {
                        template[fieldName] = field.minimum || 0;
                    } else if (field.type === 'boolean') {
                        template[fieldName] = false;
                    } else if (field.type === 'array') {
                        template[fieldName] = [];
                    } else if (field.type === 'object') {
                        template[fieldName] = {};
                    }
                }
                
                break;
            }
        }
        
        return template;
    }
    
    async show(entityType, entity, index = null, mode = 'edit') {
        this.currentEntityType = entityType;
        this.currentEntity = entity ? JSON.parse(JSON.stringify(entity)) : null;
        this.currentIndex = index;
        this.mode = mode;
        
        // Load schema for this entity type
        this.schema = await this.loadSchema(entityType);
        
        this.render();
    }
    
    render() {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.id = 'entity-editor-modal';
        
        const title = this.mode === 'create' ? 'Create New Entity' : 
                     this.mode === 'duplicate' ? 'Duplicate Entity' : 
                     'Edit Entity';
        
        overlay.innerHTML = `
            <div class="modal" style="width: 90%; max-width: 1200px;">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="btn btn-secondary btn-sm" onclick="entityEditorModal.close()">✕</button>
                </div>
                <div class="modal-body">
                    <div class="editor-tabs">
                        <button class="editor-tab active" data-tab="visual">
                            📝 Visual Editor
                        </button>
                        <button class="editor-tab" data-tab="json">
                            🔧 JSON Editor
                        </button>
                        <button class="editor-tab" data-tab="preview">
                            👁️ Preview
                        </button>
                    </div>
                    
                    <div class="editor-content">
                        <div class="editor-pane active" id="visual-editor">
                            ${this.renderVisualEditor()}
                        </div>
                        <div class="editor-pane" id="json-editor">
                            ${this.renderJsonEditor()}
                        </div>
                        <div class="editor-pane" id="preview-pane">
                            ${this.renderPreview()}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="entityEditorModal.close()">
                        Cancel
                    </button>
                    <button class="btn btn-primary" onclick="entityEditorModal.save()">
                        💾 Save Changes
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Setup tab switching
        overlay.querySelectorAll('.editor-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                overlay.querySelectorAll('.editor-tab').forEach(t => t.classList.remove('active'));
                overlay.querySelectorAll('.editor-pane').forEach(p => p.classList.remove('active'));
                
                tab.classList.add('active');
                const paneId = tab.dataset.tab + (tab.dataset.tab === 'json' ? '-editor' : 
                                                  tab.dataset.tab === 'preview' ? '-pane' : '-editor');
                document.getElementById(paneId).classList.add('active');
            });
        });
        
        // Setup JSON editor sync
        const jsonTextarea = document.getElementById('json-editor-textarea');
        if (jsonTextarea) {
            jsonTextarea.addEventListener('input', () => {
                try {
                    this.currentEntity = JSON.parse(jsonTextarea.value);
                    jsonTextarea.style.borderColor = 'var(--accent-primary)';
                } catch (e) {
                    jsonTextarea.style.borderColor = 'var(--accent-danger)';
                }
            });
        }
    }
    
    renderVisualEditor() {
        if (!this.currentEntity) {
            return '<p style="color: var(--text-secondary); padding: 20px;">Loading template...</p>';
        }
        
        // Check if ID should be immutable (always true for edit mode, false for create)
        const idImmutable = this.mode === 'edit' || this.mode === 'duplicate';
        const schemaIdImmutable = this.schema ? this.schema.id_immutable : true;
        
        const fields = Object.keys(this.currentEntity).map(key => {
            const value = this.currentEntity[key];
            const type = typeof value;
            
            // Check if this is the ID field
            const isIdField = key === 'id';
            const makeReadOnly = isIdField && idImmutable && schemaIdImmutable;
            
            if (type === 'object' && !Array.isArray(value)) {
                return `
                    <div class="form-group">
                        <label>${this.formatLabel(key)}</label>
                        <textarea class="form-control" data-field="${key}" rows="3" ${makeReadOnly ? 'readonly' : ''}>${JSON.stringify(value, null, 2)}</textarea>
                        <small style="color: var(--text-secondary);">Object field - edit as JSON</small>
                    </div>
                `;
            } else if (Array.isArray(value)) {
                return `
                    <div class="form-group">
                        <label>${this.formatLabel(key)}</label>
                        <textarea class="form-control" data-field="${key}" rows="2" ${makeReadOnly ? 'readonly' : ''}>${JSON.stringify(value)}</textarea>
                        <small style="color: var(--text-secondary);">Array field - edit as JSON</small>
                    </div>
                `;
            } else if (type === 'number') {
                return `
                    <div class="form-group">
                        <label>${this.formatLabel(key)}</label>
                        <input type="number" class="form-control" data-field="${key}" value="${value}" ${makeReadOnly ? 'readonly' : ''}>
                        ${makeReadOnly ? '<small style="color: var(--accent-warning);">⚠️ ID is immutable and cannot be changed</small>' : ''}
                    </div>
                `;
            } else if (type === 'boolean') {
                return `
                    <div class="form-group">
                        <label>
                            <input type="checkbox" data-field="${key}" ${value ? 'checked' : ''} ${makeReadOnly ? 'disabled' : ''}>
                            ${this.formatLabel(key)}
                        </label>
                    </div>
                `;
            } else {
                // String or other
                const isLongText = String(value).length > 50;
                return `
                    <div class="form-group">
                        <label>${this.formatLabel(key)}</label>
                        ${isLongText ? 
                            `<textarea class="form-control" data-field="${key}" rows="3" ${makeReadOnly ? 'readonly' : ''}>${value}</textarea>` :
                            `<input type="text" class="form-control" data-field="${key}" value="${value}" ${makeReadOnly ? 'readonly' : ''}>`
                        }
                        ${makeReadOnly && isIdField ? '<small style="color: var(--accent-warning);">⚠️ ID is immutable and cannot be changed</small>' : ''}
                    </div>
                `;
            }
        }).join('');
        
        return `
            <div class="visual-editor-form">
                ${fields}
            </div>
        `;
    }
    
    renderJsonEditor() {
        const json = this.currentEntity ? JSON.stringify(this.currentEntity, null, 2) : '{}';
        
        return `
            <div class="json-editor-container">
                <textarea id="json-editor-textarea" class="form-control" style="font-family: 'Courier New', monospace; min-height: 400px;">${json}</textarea>
                <div style="margin-top: 10px;">
                    <button class="btn btn-secondary btn-sm" onclick="entityEditorModal.formatJson()">
                        ✨ Format JSON
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="entityEditorModal.validateJson()">
                        ✔️ Validate
                    </button>
                </div>
            </div>
        `;
    }
    
    renderPreview() {
        if (!this.currentEntity) {
            return '<p style="color: var(--text-secondary); padding: 20px;">No entity to preview</p>';
        }
        
        return `
            <div class="preview-container">
                <div class="card" style="max-width: 400px; margin: 20px auto;">
                    <div class="card-header">
                        <div class="card-title">${this.currentEntity.name || 'Unnamed Entity'}</div>
                        ${this.currentEntity.rarity ? `<div class="card-badge badge-${this.currentEntity.rarity}">${this.currentEntity.rarity}</div>` : ''}
                    </div>
                    <div class="card-content">
                        <p>${this.currentEntity.description || 'No description'}</p>
                        <div style="margin-top: 12px; font-size: 12px; color: var(--text-secondary);">
                            <strong>ID:</strong> ${this.currentEntity.id || 'N/A'}<br>
                            ${this.currentEntity.cost ? `<strong>Cost:</strong> $${this.currentEntity.cost}<br>` : ''}
                            ${this.currentEntity.unlock_level ? `<strong>Unlock Level:</strong> ${this.currentEntity.unlock_level}<br>` : ''}
                        </div>
                    </div>
                </div>
                
                <details style="margin: 20px; padding: 20px; background: var(--bg-tertiary); border-radius: 8px;">
                    <summary style="cursor: pointer; font-weight: 600; margin-bottom: 10px;">Full JSON Data</summary>
                    <pre style="font-size: 12px; overflow-x: auto;">${JSON.stringify(this.currentEntity, null, 2)}</pre>
                </details>
            </div>
        `;
    }
    
    formatLabel(key) {
        return key.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
    formatJson() {
        const textarea = document.getElementById('json-editor-textarea');
        try {
            const obj = JSON.parse(textarea.value);
            textarea.value = JSON.stringify(obj, null, 2);
            this.controlPanel.showToast('Success', 'JSON formatted', 'success');
        } catch (e) {
            this.controlPanel.showToast('Error', 'Invalid JSON: ' + e.message, 'error');
        }
    }
    
    validateJson() {
        const textarea = document.getElementById('json-editor-textarea');
        try {
            JSON.parse(textarea.value);
            this.controlPanel.showToast('Success', 'JSON is valid', 'success');
            textarea.style.borderColor = 'var(--accent-primary)';
        } catch (e) {
            this.controlPanel.showToast('Error', 'Invalid JSON: ' + e.message, 'error');
            textarea.style.borderColor = 'var(--accent-danger)';
        }
    }
    
    async save() {
        // Collect data from active editor
        const jsonEditor = document.getElementById('json-editor-textarea');
        if (jsonEditor) {
            try {
                this.currentEntity = JSON.parse(jsonEditor.value);
            } catch (e) {
                this.controlPanel.showToast('Error', 'Invalid JSON: ' + e.message, 'error');
                return;
            }
        }
        
        // Collect data from visual editor
        const visualEditor = document.querySelector('.visual-editor-form');
        if (visualEditor) {
            visualEditor.querySelectorAll('[data-field]').forEach(input => {
                const field = input.dataset.field;
                
                // Skip readonly fields (like ID in edit mode)
                if (input.hasAttribute('readonly') || input.hasAttribute('disabled')) {
                    return;
                }
                
                if (input.type === 'checkbox') {
                    this.currentEntity[field] = input.checked;
                } else if (input.type === 'number') {
                    this.currentEntity[field] = parseFloat(input.value);
                } else {
                    const value = input.value;
                    // Try to parse as JSON for objects/arrays
                    try {
                        if (value.startsWith('{') || value.startsWith('[')) {
                            this.currentEntity[field] = JSON.parse(value);
                        } else {
                            this.currentEntity[field] = value;
                        }
                    } catch (e) {
                        this.currentEntity[field] = value;
                    }
                }
            });
        }
        
        // Validate against schema before saving
        if (this.schema) {
            try {
                const validateResponse = await fetch(`${API_BASE}/schemas/${this.currentEntityType}/validate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ entity: this.currentEntity })
                });
                
                const validateData = await validateResponse.json();
                
                if (!validateData.valid) {
                    const errorMsg = validateData.errors ? validateData.errors.join(', ') : validateData.message;
                    this.controlPanel.showToast('Validation Error', errorMsg, 'error');
                    return;
                }
            } catch (error) {
                console.warn('Schema validation failed:', error);
                // Continue with save even if validation endpoint fails
            }
        }
        
        // Save via API
        try {
            let response;
            if (this.mode === 'create' || this.mode === 'duplicate') {
                // Create new entity
                response = await fetch(`${API_BASE}/entities/${this.currentEntityType}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ entity: this.currentEntity })
                });
            } else {
                // Update existing entity
                const entityId = this.currentEntity.id;
                response = await fetch(`${API_BASE}/entities/${this.currentEntityType}/${entityId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ entity: this.currentEntity })
                });
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.controlPanel.showToast('Success', `Entity ${this.mode === 'create' ? 'created' : 'updated'} successfully`, 'success');
                await this.controlPanel.loadAllData();
                this.controlPanel.refreshCurrentView();
                this.close();
            } else {
                this.controlPanel.showToast('Error', data.message, 'error');
            }
        } catch (error) {
            this.controlPanel.showToast('Error', 'Failed to save entity: ' + error.message, 'error');
        }
    }
    
    close() {
        const modal = document.getElementById('entity-editor-modal');
        if (modal) {
            modal.remove();
        }
    }
}

// Initialize global editor instance
let entityEditorModal;
document.addEventListener('DOMContentLoaded', () => {
    // Wait for controlPanel to be initialized
    setTimeout(() => {
        if (typeof controlPanel !== 'undefined') {
            entityEditorModal = new EntityEditorModal(controlPanel);
        }
    }, 100);
});
