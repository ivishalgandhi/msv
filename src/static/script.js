document.addEventListener('DOMContentLoaded', function() {
    const sourceFile = document.getElementById('sourceFile');
    const destFile = document.getElementById('destFile');
    const matchColumn = document.getElementById('matchColumn');
    const columnCheckboxes = document.getElementById('columnCheckboxes');
    const joinType = document.getElementById('joinType');
    const ignoreCase = document.getElementById('ignoreCase');
    const mergeButton = document.getElementById('mergeButton');
    const sourceSheet = document.getElementById('sourceSheet');
    const destSheet = document.getElementById('destSheet');
    const sourceSheetSelect = document.getElementById('sourceSheetSelect');
    const destSheetSelect = document.getElementById('destSheetSelect');
    // const themeSelector = document.getElementById('themeSelector'); // Removed duplicate declaration
    
    let sourceColumns = [];
    let destColumns = [];

    // Source File Change Handler
    sourceFile.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (file) {
            // Reset sheet selection
            sourceSheetSelect.classList.add('d-none');
            sourceSheet.innerHTML = '';

            if (file.name.endsWith('.xlsx')) {
                // Get available sheets for Excel files
                const sheets = await getSheets(file, 'source');
                if (sheets && sheets.length) {
                    sourceSheetSelect.classList.remove('d-none');
                    sourceSheet.innerHTML = `
                        ${sheets.map(sheet => `<option value="${sheet}">${sheet}</option>`).join('')}
                    `;
                    // Select the first sheet by default
                    sourceSheet.value = sheets[0];
                }
            }

            // Preview file with the selected sheet (first sheet by default)
            await previewFile(file, 'sourcePreview', true, sourceSheet.value);
        }
    });

    // Destination File Change Handler
    destFile.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (file) {
            // Reset sheet selection
            destSheetSelect.classList.add('d-none');
            destSheet.innerHTML = '';

            if (file.name.endsWith('.xlsx')) {
                // Get available sheets for Excel files
                const sheets = await getSheets(file, 'destination');
                if (sheets && sheets.length) {
                    destSheetSelect.classList.remove('d-none');
                    destSheet.innerHTML = `
                        ${sheets.map(sheet => `<option value="${sheet}">${sheet}</option>`).join('')}
                    `;
                    // Select the first sheet by default
                    destSheet.value = sheets[0];
                }
            }

            // Preview file with the selected sheet (first sheet by default)
            await previewFile(file, 'destPreview', false, destSheet.value);
        }
    });

    async function handleFileSelect(file, previewId, isSource) {
        // Get preview element first
        const preview = document.getElementById(previewId);
        
        // Show loading state
        preview.innerHTML = `
            <div class="d-flex justify-content-center align-items-center p-4">
                <div class="spinner-border text-primary"></div>
            </div>`;

        try {
            // Check if Excel file
            if (file.name.endsWith('.xlsx')) {
                const sheets = await getSheets(file, isSource ? 'source' : 'destination');
                if (sheets && sheets.length) {
                    const sheetSelect = document.getElementById(isSource ? 'sourceSheetSelect' : 'destSheetSelect');
                    const sheetElement = document.getElementById(isSource ? 'sourceSheet' : 'destSheet');
                    
                    sheetSelect.classList.remove('d-none');
                    sheetElement.innerHTML = `
                        <option value="">Select Sheet</option>
                        ${sheets.map(sheet => `<option value="${sheet}">${sheet}</option>`).join('')}
                    `;
                    
                    // Add sheet change listener
                    sheetElement.addEventListener('change', () => {
                        if (sheetElement.value) {
                            previewFile(file, previewId, isSource, sheetElement.value);
                        }
                    });
                }
            }
            
            // Preview file contents
            await previewFile(file, previewId, isSource);
            
        } catch (error) {
            console.error('File handling error:', error);
            preview.innerHTML = `
                <div class="alert alert-danger m-3">
                    Error handling file: ${error.message}
                </div>`;
        }
    }

    // Preview file function
    async function previewFile(file, previewId, isSource, sheetName = null) {
        const preview = document.getElementById(previewId);
        
        // Show loading spinner
        preview.innerHTML = `
            <div class="d-flex justify-content-center align-items-center p-4">
                <div class="spinner-border text-primary"></div>
            </div>`;

        if (!file) {
            preview.innerHTML = '<div class="alert alert-info m-3">No file selected</div>';
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', isSource ? 'source' : 'destination');
        
        // Add sheet name if provided
        if (sheetName) {
            formData.append('sheet', sheetName);
        }

        try {
            const response = await fetch('/preview', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                preview.innerHTML = `<div class="alert alert-danger m-3">${escapeHtml(data.error)}</div>`;
                return;
            }

            // Store columns
            if (isSource) {
                sourceColumns = data.columns;
            } else {
                destColumns = data.columns;
            }

            // Find matching columns
            const matchingColumns = data.columns.filter(col => 
                isSource ? 
                    destColumns.some(destCol => destCol.toLowerCase() === col.toLowerCase()) :
                    sourceColumns.some(sourceCol => sourceCol.toLowerCase() === col.toLowerCase())
            );

            // Show preview with highlighted matching columns
            preview.innerHTML = `
                <div class="preview-info">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>Total Columns:</strong> ${data.columns.length}
                            <strong class="ms-3">Total Rows:</strong> ${data.total_rows}
                        </div>
                        ${matchingColumns.length ? `
                            <span class="badge bg-success">
                                ${matchingColumns.length} Matching Columns
                            </span>
                        ` : ''}
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-sm preview-table">
                        <thead>
                            <tr>
                                ${data.columns.map(col => `
                                    <th class="${matchingColumns.includes(col) ? 'matching-column' : ''}">
                                        ${escapeHtml(col)}
                                        ${matchingColumns.includes(col) ? 
                                            '<i class="bi bi-link text-success ms-1"></i>' : 
                                            ''}
                                    </th>
                                `).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${data.preview.map(row => `
                                <tr>
                                    ${data.columns.map(col => `
                                        <td class="${matchingColumns.includes(col) ? 'matching-column' : ''}">
                                            ${escapeHtml(row[col] || '')}
                                        </td>
                                    `).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;

            // Update match column options
            updateMatchColumns();

        } catch (error) {
            console.error('Preview error:', error);
            preview.innerHTML = `
                <div class="alert alert-danger m-3">
                    Error previewing file: ${error.message}
                </div>`;
        }
    }

    // Get sheets from Excel file
    async function getSheets(file, type) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);

        const response = await fetch('/getsheets', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.error) {
            console.error('Error getting sheets:', data.error);
            return [];
        }
        return data.sheets || [];
    }

    // Helper function to escape HTML
    function escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) {
            return '';
        }
        return String(unsafe)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Update match column options
    function updateMatchColumns() {
        if (sourceColumns.length && destColumns.length) {
            // Get common columns using case-insensitive comparison
            const commonColumns = sourceColumns.filter(sourceCol => 
                destColumns.some(destCol => 
                    sourceCol.toLowerCase() === destCol.toLowerCase()
                )
            );

            // Create options with original column names
            matchColumn.innerHTML = `
                <option value="">Select Match Column</option>
                ${commonColumns.map(col => {
                    // Find the matching destination column
                    const destCol = destColumns.find(dc => 
                        dc.toLowerCase() === col.toLowerCase()
                    );
                    return `<option value="${col}">
                        ${col}${destCol !== col ? ` (matches ${destCol})` : ''}
                    </option>`;
                }).join('')}
            `;

            updateColumnSelection();
        }
    }

    // Update column selection checkboxes
    function updateColumnSelection() {
        if (sourceColumns.length) {
            columnCheckboxes.innerHTML = sourceColumns.map(col => `
                <div class="column-checkbox">
                    <label>
                        <input type="checkbox" name="columns" value="${col}">
                        ${col}
                    </label>
                </div>
            `).join('');
        }
    }

    // Handle merge button click
    mergeButton.addEventListener('click', async function() {
        if (!sourceFile.files[0] || !destFile.files[0]) {
            alert('Please select both source and destination files');
            return;
        }

        if (!matchColumn.value) {
            alert('Please select a match column');
            return;
        }

        const selectedColumns = Array.from(document.querySelectorAll('input[name="columns"]:checked'))
            .map(cb => cb.value);

        if (!selectedColumns.length) {
            alert('Please select columns to copy');
            return;
        }

        // Show loading state
        document.getElementById('result').innerHTML = `
            <div class="alert alert-info">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2"></div>
                    Processing merge...
                </div>
            </div>`;

        const formData = new FormData();
        formData.append('source', sourceFile.files[0]);
        formData.append('destination', destFile.files[0]);

        // Find exact match first, then case-insensitive match
        const destCol = destColumns.find(dc => dc === matchColumn.value) || 
                       destColumns.find(dc => dc.toLowerCase() === matchColumn.value.toLowerCase());
        
        // Use exact column name from destination
        formData.append('match_column', destCol || matchColumn.value);

        // Find and use exact column names from destination
        selectedColumns.forEach(col => {
            const matchingDestCol = destColumns.find(dc => dc === col) || 
                                  destColumns.find(dc => dc.toLowerCase() === col.toLowerCase());
            formData.append('columns[]', matchingDestCol || col);
        });

        formData.append('join_type', joinType.value);
        formData.append('ignore_case', 'true');  // Enable case-insensitive matching

        // Add sheet information if Excel files
        if (sourceFile.files[0].name.endsWith('.xlsx') && sourceSheet.value) {
            formData.append('source_sheet', sourceSheet.value);
        }
        if (destFile.files[0].name.endsWith('.xlsx') && destSheet.value) {
            formData.append('dest_sheet', destSheet.value);
        }

        try {
            const response = await fetch('/merge', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                document.getElementById('result').innerHTML = `
                    <div class="alert alert-success">
                        <h6 class="mb-2">✨ Merge completed successfully!</h6>
                        <div class="small">
                            <div>Rows: ${data.stats.rows_before} → ${data.stats.rows_after} 
                                (${data.stats.rows_changed >= 0 ? '+' : ''}${data.stats.rows_changed})</div>
                            ${data.stats.new_columns.length ? 
                                `<div>New columns: ${data.stats.new_columns.join(', ')}</div>` : ''}
                            <div>Matched rows: ${data.stats.matched_rows}</div>
                        </div>
                    </div>`;
            } else {
                document.getElementById('result').innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Error: ${data.error}
                    </div>`;
            }
        } catch (error) {
            console.error('Merge error:', error);
            document.getElementById('result').innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Error performing merge: ${error.message}
                </div>`;
        }
    });

    // Update sheet change handlers
    sourceSheet.addEventListener('change', function() {
        const file = sourceFile.files[0];
        if (file) {
            previewFile(file, 'sourcePreview', true, this.value);
        }
    });

    destSheet.addEventListener('change', function() {
        const file = destFile.files[0];
        if (file) {
            previewFile(file, 'destPreview', false, this.value);
        }
    });

    // Initialize dark mode
    const darkMode = localStorage.getItem('darkMode') === 'true';
    document.documentElement.setAttribute('data-bs-theme', darkMode ? 'dark' : 'light');
    updateDarkModeIcon(darkMode);

    // Dark mode toggle handler
    document.getElementById('darkModeToggle').addEventListener('click', function() {
        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        const newMode = !isDark;
        document.documentElement.setAttribute('data-bs-theme', newMode ? 'dark' : 'light');
        localStorage.setItem('darkMode', newMode);
        updateDarkModeIcon(newMode);
    });

    function updateDarkModeIcon(isDark) {
        const icon = document.querySelector('#darkModeToggle i');
        icon.className = isDark ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }

    // Focus view handlers
    document.querySelectorAll('.focus-view-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-preview-target');
            const sourceContent = document.getElementById(targetId);
            
            if (!sourceContent) {
                console.error(`Preview content not found for ${targetId}`);
                return;
            }
            
            // Get modal elements
            const modal = document.getElementById('focusViewModal');
            if (!modal) {
                console.error('Focus view modal not found');
                return;
            }
            
            const focusContent = modal.querySelector('#focusViewContent');
            const modalTitle = modal.querySelector('.modal-title');
            
            // Set modal content and title
            focusContent.innerHTML = sourceContent.innerHTML;
            modalTitle.textContent = `${targetId === 'sourcePreview' ? 'Source' : 'Destination'} File Preview`;
            
            // Show modal using Bootstrap
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
        });
    });

    // Theme handling
    const themeSelector = document.getElementById('themeSelector');

    // Get system theme
    const getSystemTheme = () => {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    // Get preferred theme
    const getPreferredTheme = () => {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme) return storedTheme;
        return 'auto';
    };

    // Apply theme
    const applyTheme = (theme) => {
        const effectiveTheme = theme === 'auto' ? getSystemTheme() : theme;
        document.documentElement.setAttribute('data-bs-theme', effectiveTheme);
    };

    // Initialize theme
    const theme = getPreferredTheme();
    themeSelector.value = theme;
    applyTheme(theme);

    // Handle theme changes
    themeSelector.addEventListener('change', () => {
        const selectedTheme = themeSelector.value;
        localStorage.setItem('theme', selectedTheme);
        applyTheme(selectedTheme);
    });

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (themeSelector.value === 'auto') {
            applyTheme('auto');
        }
    });

    // Focus view handling
    const focusViewModal = document.getElementById('focusViewModal');
    
    if (focusViewModal) {
        focusViewModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const previewId = button.getAttribute('data-preview-target');
            const sourceContent = document.getElementById(previewId);
            
            // Update modal content
            const modalTitle = this.querySelector('.modal-title');
            const modalContent = this.querySelector('#focusViewContent');
            
            modalTitle.textContent = `${previewId === 'sourcePreview' ? 'Source' : 'Destination'} File Preview`;
            if (sourceContent) {
                modalContent.innerHTML = sourceContent.innerHTML;
            } else {
                modalContent.innerHTML = '<div class="alert alert-warning m-3">No content to display</div>';
            }
        });
    }
});

// Focus view handling
document.querySelectorAll('.focus-view-btn').forEach(btn => {
    btn.addEventListener('click', async function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('data-preview-target');
        
        // Get file input and sheet selector
        const fileInput = document.getElementById(
            targetId === 'sourcePreview' ? 'sourceFile' : 'destFile'
        );
        const sheetSelect = document.getElementById(
            targetId === 'sourcePreview' ? 'sourceSheet' : 'destSheet'
        );
        
        if (!fileInput.files[0]) {
            console.error('No file selected');
            return;
        }
        
        // Show loading state in modal
        const modal = document.getElementById('focusViewModal');
        const modalContent = modal.querySelector('#focusViewContent');
        const focusViewSheet = document.getElementById('focusViewSheet');
        const focusViewSheetSelect = document.getElementById('focusViewSheetSelect');
        
        modalContent.innerHTML = `
            <div class="d-flex justify-content-center align-items-center p-4">
                <div class="spinner-border text-primary"></div>
            </div>`;
            
        // Show modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        
        // Load full preview
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('type', targetId === 'sourcePreview' ? 'source' : 'destination');
        formData.append('focus', 'true');
        
        // Add current sheet if Excel file
        if (fileInput.files[0].name.endsWith('.xlsx') && sheetSelect.value) {
            formData.append('sheet', sheetSelect.value);
        }
        
        try {
            const response = await fetch('/preview', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                modalContent.innerHTML = `
                    <div class="alert alert-danger m-3">${escapeHtml(data.error)}</div>`;
                return;
            }
            
            // Update sheet selector if Excel file
            if (data.is_excel) {
                focusViewSheetSelect.classList.remove('d-none');
                focusViewSheet.innerHTML = data.available_sheets.map(sheet => `
                    <option value="${sheet}" ${sheet === data.current_sheet ? 'selected' : ''}>
                        ${sheet}
                    </option>
                `).join('');
                
                // Add sheet change handler
                focusViewSheet.onchange = async () => {
                    const formData = new FormData();
                    formData.append('file', fileInput.files[0]);
                    formData.append('type', targetId === 'sourcePreview' ? 'source' : 'destination');
                    formData.append('focus', 'true');
                    formData.append('sheet', focusViewSheet.value);
                    
                    // Update preview with new sheet
                    await loadFocusView(formData, modalContent);
                };
            } else {
                focusViewSheetSelect.classList.add('d-none');
            }
            
            // Update title
            modal.querySelector('.modal-title').textContent = 
                `${targetId === 'sourcePreview' ? 'Source' : 'Destination'} File Preview` +
                (data.is_excel ? ` - Sheet: ${data.current_sheet}` : '');
            
            // Show preview
            await loadFocusView(formData, modalContent);
            
        } catch (error) {
            modalContent.innerHTML = `
                <div class="alert alert-danger m-3">
                    Error loading preview: ${error.message}
                </div>`;
        }
    });
});

// Helper function to load focus view content
async function loadFocusView(formData, container) {
    try {
        const response = await fetch('/preview', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `
                <div class="alert alert-danger m-3">${escapeHtml(data.error)}</div>`;
            return;
        }
        
        container.innerHTML = `
            <div class="preview-info sticky-top">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>Total Columns:</strong> ${data.columns.length}
                        <strong class="ms-3">Total Rows:</strong> ${data.total_rows}
                    </div>
                </div>
            </div>
            <div class="table-responsive">
                <table class="table table-sm preview-table">
                    <thead>
                        <tr>
                            ${data.columns.map(col => `<th>${escapeHtml(col)}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${data.preview.map(row => `
                            <tr>
                                ${data.columns.map(col => `<td>${escapeHtml(row[col] || '')}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>`;
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger m-3">
                Error loading preview: ${error.message}
            </div>`;
    }
}

function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/<//g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Source Sheet Change
sourceSheet.addEventListener('change', function() {
    const file = sourceFile.files[0];
    if (file) {
        previewFile(file, 'sourcePreview', true, this.value);
    }
});

// Destination Sheet Change
destSheet.addEventListener('change', function() {
    const file = destFile.files[0];
    if (file) {
        previewFile(file, 'destPreview', false, this.value);
    }
});