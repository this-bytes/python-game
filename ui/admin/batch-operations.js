/**
 * Batch Operations System
 * 
 * Provides bulk operations on game entities:
 * - Batch edit multiple entities at once
 * - Mass delete with filters
 * - Bulk stat modifications
 * - Template application to multiple entities
 */

class BatchOperations {
    constructor(controlPanel) {
        this.controlPanel = controlPanel;
        this.selectedEntities = new Set();
        this.currentEntityType = null;
    }
    
    showBatchEditor(entityType) {
        this.currentEntityType = entityType;
        this.selectedEntities.clear();
        
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.id = 'batch-operations-modal';
        
        overlay.innerHTML = `
            <div class="modal" style="width: 90%; max-width: 1400px;">
                <div class="modal-header">
                    <h3>⚡ Batch Operations - ${entityType}</h3>
                    <button class="btn btn-secondary btn-sm" onclick="batchOperations.close()">✕</button>
                </div>
                <div class="modal-body">
                    <div class="grid grid-2" style="margin-bottom: 20px;">
                        <div class="panel">
                            <div class="panel-header">
                                <h3>Select Entities</h3>
                                <button class="btn btn-secondary btn-sm" onclick="batchOperations.selectAll()">
                                    Select All
                                </button>
                            </div>
                            <div id="batch-entity-list" style="max-height: 400px; overflow-y: auto;">
                                ${this.renderEntityList(entityType)}
                            </div>
                        </div>
                        
                        <div class="panel">
                            <div class="panel-header">
                                <h3>Operations</h3>
                                <div style="color: var(--text-secondary); font-size: 12px;">
                                    <span id="selected-count">0</span> entities selected
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Operation Type</label>
                                <select class="form-control" id="batch-operation-type" onchange="batchOperations.updateOperationForm()">
                                    <option value="">-- Select Operation --</option>
                                    <option value="update-field">Update Field</option>
                                    <option value="multiply-stat">Multiply Stat</option>
                                    <option value="add-to-stat">Add to Stat</option>
                                    <option value="change-rarity">Change Rarity</option>
                                    <option value="adjust-cost">Adjust Cost</option>
                                    <option value="delete">Delete Selected</option>
                                </select>
                            </div>
                            
                            <div id="operation-form-container">
                                <p style="color: var(--text-secondary); padding: 20px;">Select an operation type</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="batchOperations.close()">
                        Cancel
                    </button>
                    <button class="btn btn-danger" onclick="batchOperations.clearSelection()">
                        Clear Selection
                    </button>
                    <button class="btn btn-primary" onclick="batchOperations.executeBatchOperation()">
                        ⚡ Execute Operation
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
    }
    
    renderEntityList(entityType) {
        const data = this.controlPanel.entities[entityType] || {};
        let entities = [];
        
        // Extract entities array
        if (Array.isArray(data)) {
            entities = data;
        } else if (data.incident_types) {
            entities = data.incident_types;
        } else if (data.specialist_archetypes) {
            entities = data.specialist_archetypes;
        } else if (data.equipment) {
            entities = data.equipment;
        } else if (data.facilities) {
            entities = data.facilities;
        } else if (data.automation_scripts) {
            entities = data.automation_scripts;
        } else if (data.achievements) {
            entities = data.achievements;
        }
        
        if (entities.length === 0) {
            return '<p style="color: var(--text-secondary); padding: 20px;">No entities found</p>';
        }
        
        return entities.map((entity, index) => {
            const id = entity.id || `entity_${index}`;
            const name = entity.name || id;
            
            return `
                <div class="batch-entity-item" style="padding: 10px; border-bottom: 1px solid var(--border-color);">
                    <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                        <input type="checkbox" class="batch-entity-checkbox" data-entity-id="${id}" 
                               onchange="batchOperations.toggleEntity('${id}')">
                        <div style="flex: 1;">
                            <div style="font-weight: 600;">${name}</div>
                            <div style="font-size: 12px; color: var(--text-secondary);">${entity.description || ''}</div>
                        </div>
                        ${entity.rarity ? `<div class="card-badge badge-${entity.rarity}">${entity.rarity}</div>` : ''}
                    </label>
                </div>
            `;
        }).join('');
    }
    
    toggleEntity(entityId) {
        if (this.selectedEntities.has(entityId)) {
            this.selectedEntities.delete(entityId);
        } else {
            this.selectedEntities.add(entityId);
        }
        this.updateSelectedCount();
    }
    
    selectAll() {
        const checkboxes = document.querySelectorAll('.batch-entity-checkbox');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = !allChecked;
            const entityId = checkbox.dataset.entityId;
            if (!allChecked) {
                this.selectedEntities.add(entityId);
            } else {
                this.selectedEntities.delete(entityId);
            }
        });
        
        this.updateSelectedCount();
    }
    
    clearSelection() {
        this.selectedEntities.clear();
        document.querySelectorAll('.batch-entity-checkbox').forEach(cb => {
            cb.checked = false;
        });
        this.updateSelectedCount();
    }
    
    updateSelectedCount() {
        const countElement = document.getElementById('selected-count');
        if (countElement) {
            countElement.textContent = this.selectedEntities.size;
        }
    }
    
    updateOperationForm() {
        const operationType = document.getElementById('batch-operation-type').value;
        const container = document.getElementById('operation-form-container');
        
        let formHTML = '';
        
        switch(operationType) {
            case 'update-field':
                formHTML = `
                    <div class="form-group">
                        <label>Field Name</label>
                        <input type="text" class="form-control" id="batch-field-name" placeholder="e.g., description">
                    </div>
                    <div class="form-group">
                        <label>New Value</label>
                        <input type="text" class="form-control" id="batch-field-value">
                    </div>
                `;
                break;
                
            case 'multiply-stat':
                formHTML = `
                    <div class="form-group">
                        <label>Stat Field</label>
                        <input type="text" class="form-control" id="batch-stat-field" placeholder="e.g., base_reward">
                    </div>
                    <div class="form-group">
                        <label>Multiplier</label>
                        <input type="number" class="form-control" id="batch-multiplier" value="1.5" step="0.1">
                    </div>
                `;
                break;
                
            case 'add-to-stat':
                formHTML = `
                    <div class="form-group">
                        <label>Stat Field</label>
                        <input type="text" class="form-control" id="batch-stat-field" placeholder="e.g., cost">
                    </div>
                    <div class="form-group">
                        <label>Amount to Add</label>
                        <input type="number" class="form-control" id="batch-add-amount" value="0">
                    </div>
                `;
                break;
                
            case 'change-rarity':
                formHTML = `
                    <div class="form-group">
                        <label>New Rarity</label>
                        <select class="form-control" id="batch-new-rarity">
                            <option value="common">Common</option>
                            <option value="rare">Rare</option>
                            <option value="epic">Epic</option>
                            <option value="legendary">Legendary</option>
                        </select>
                    </div>
                `;
                break;
                
            case 'adjust-cost':
                formHTML = `
                    <div class="form-group">
                        <label>Adjustment Type</label>
                        <select class="form-control" id="batch-cost-type">
                            <option value="multiply">Multiply by</option>
                            <option value="add">Add</option>
                            <option value="set">Set to</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Value</label>
                        <input type="number" class="form-control" id="batch-cost-value" value="0">
                    </div>
                `;
                break;
                
            case 'delete':
                formHTML = `
                    <div style="padding: 20px; background: var(--bg-tertiary); border-radius: 8px; border-left: 4px solid var(--accent-danger);">
                        <p style="color: var(--accent-danger); font-weight: 600; margin-bottom: 10px;">
                            ⚠️ WARNING: Permanent Deletion
                        </p>
                        <p style="color: var(--text-secondary); font-size: 14px;">
                            This will permanently delete ${this.selectedEntities.size} selected entities. 
                            This action cannot be undone. A backup will be created.
                        </p>
                    </div>
                `;
                break;
                
            default:
                formHTML = '<p style="color: var(--text-secondary); padding: 20px;">Select an operation type</p>';
        }
        
        container.innerHTML = formHTML;
    }
    
    async executeBatchOperation() {
        if (this.selectedEntities.size === 0) {
            this.controlPanel.showToast('Error', 'No entities selected', 'error');
            return;
        }
        
        const operationType = document.getElementById('batch-operation-type').value;
        if (!operationType) {
            this.controlPanel.showToast('Error', 'Please select an operation type', 'error');
            return;
        }
        
        const entityIds = Array.from(this.selectedEntities);
        let updateData = {};
        
        switch(operationType) {
            case 'update-field':
                const fieldName = document.getElementById('batch-field-name').value;
                const fieldValue = document.getElementById('batch-field-value').value;
                updateData[fieldName] = fieldValue;
                break;
                
            case 'change-rarity':
                updateData.rarity = document.getElementById('batch-new-rarity').value;
                break;
                
            // For complex operations, we need to handle them differently
            case 'multiply-stat':
            case 'add-to-stat':
            case 'adjust-cost':
                this.controlPanel.showToast('Info', 'Complex operations coming soon', 'warning');
                return;
        }
        
        try {
            const response = await fetch(`${API_BASE}/entities/${this.currentEntityType}/batch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    operation: operationType === 'delete' ? 'delete' : 'update',
                    entity_ids: entityIds,
                    data: updateData
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.controlPanel.showToast('Success', `Batch operation completed: ${data.affected_count} entities affected`, 'success');
                await this.controlPanel.loadAllData();
                this.controlPanel.refreshCurrentView();
                this.close();
            } else {
                this.controlPanel.showToast('Error', data.message, 'error');
            }
        } catch (error) {
            this.controlPanel.showToast('Error', 'Batch operation failed: ' + error.message, 'error');
        }
    }
    
    close() {
        const modal = document.getElementById('batch-operations-modal');
        if (modal) {
            modal.remove();
        }
    }
}

// Initialize global instance
let batchOperations;
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (typeof controlPanel !== 'undefined') {
            batchOperations = new BatchOperations(controlPanel);
        }
    }, 100);
});
