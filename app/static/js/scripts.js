function updateFileName(inputId, buttonId) {
    const input = document.getElementById(inputId);
    const button = document.getElementById(buttonId);
    if (input.files.length > 0) {
        button.textContent = input.files[0].name;
    } else {
        button.textContent = 'Select File';
    }
}

// Make buttons work with input fields
function toggleEdit(type, index) {
    const label = document.getElementById(`label_${type}_${index}`);
    const input = document.getElementById(`input_${type}_${index}`);

    if (label.classList.contains("hidden")) {
        label.classList.remove("hidden");
        input.classList.add("hidden");
        label.textContent = input.value;
    } else {
        label.classList.add("hidden");
        input.classList.remove("hidden");
        input.focus();
        input.select();
    }
}

// Make edit button work with multiple location input fields
function toggleEditLocation(type, index) {
    const labels = document.querySelectorAll(`[data-label="${type}_${index}"]`);
    const inputs = document.querySelectorAll(`[data-input="${type}_${index}"]`);

    labels.forEach((label, i) => {
        if (label.classList.contains("hidden")) {
            label.classList.remove("hidden");
            inputs[i].classList.add("hidden");
            label.textContent = inputs[i].value;
        } else {
            label.classList.add("hidden");
            inputs[i].classList.remove("hidden");
            inputs[i].focus();
            inputs[i].select();
        }
    });
}

// Add rows with 4 inputs per row
document.getElementById("addRowButton").addEventListener("click", function () {
    const container = document.getElementById("location_container");
    const newIndex = container.children.length + 1; // Unique index for the new row

    const newRow = document.createElement("div");
    newRow.classList.add("flex", "justify-evenly", "items-center", "border-b");
    newRow.id = `row_${newIndex}`;

    newRow.innerHTML = `
                          <label data-label="tax_${newIndex}"
                        class="p-3 w-full font-semibold break-words text-xl">
                        
                      </label>
                      <input data-input="tax_${newIndex}"
                        class="border border-gray-300 text-black text-xl p-3 w-full rounded-lg focus:outline-none hidden"
                        type="text" name="data_tax_4_location_start_date_${newIndex}" value="">

                      <label data-label="tax_${newIndex}"
                        class="p-3 w-full font-semibold break-words text-xl">
                        
                      </label>
                      <input data-input="tax_${newIndex}"
                        class="border border-gray-300 text-black text-xl p-3 w-full rounded-lg focus:outline-none hidden"
                        type="text" name="data_tax_4_location_end_date_${newIndex}" value="">

                      <label data-label="tax_${newIndex}"
                        class="p-3 w-full font-semibold break-words text-xl">
                        
                      </label>
                      <input data-input="tax_${newIndex}"
                        class="border border-gray-300 text-black text-xl p-3 w-full rounded-lg focus:outline-none hidden"
                        type="text" name="data_tax_4_location_city_${newIndex}" value="">

                      <label data-label="tax_${newIndex}"
                        class="p-3 w-full font-semibold break-words text-xl">
                        
                      </label>
                      
                      <input data-input="tax_${newIndex}"
                        class="border border-gray-300 text-black text-xl p-3 w-full rounded-lg focus:outline-none hidden"
                        type="text" name="data_tax_4_location_country_${newIndex}" value="">
                   
                      <div class="flex justify-end w-full">
                      <!-- Edit Button -->
                      <button type="button"
                        class="bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold py-3 px-4 m-2 rounded-lg shadow-md transition-all duration-300"
                        onclick="toggleEditLocation('tax', ${newIndex})">
                        wijzig
                      </button>

                      <!-- Remove Button -->
                      <button type="button"
                        class="bg-red-600 hover:bg-red-700 text-white text-xl font-semibold py-3 px-4 m-2 rounded-lg shadow-md transition-all duration-300"
                        onclick="removeRow('row_${newIndex}')">
                        x
                      </button>
                      </div>

    `;

    container.appendChild(newRow);
});


function removeRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.remove();
    }
}
// Function to hide secondary fields unless the primary label has text.
function hideSecondaryBlock(labelId, hiddenFieldId) {

    function checkLabelText() {
        let label = document.getElementById(labelId);
        let hiddenField = document.getElementById(hiddenFieldId);

        if (!label || !hiddenField) return; // Prevent errors if elements are missing

        if (label.textContent.trim() === "" | label.textContent === "None") {
            hiddenField.style.display = "none";
        } else {
            hiddenField.style.display = "block";
        }
    }

    // Run check on page load
    window.addEventListener("DOMContentLoaded", checkLabelText);

    // Observe label text changes
    const observer = new MutationObserver(() => checkLabelText());
    observer.observe(document.getElementById(labelId), { childList: true, subtree: true });

    // Run check immediately in case script loads after DOMContentLoaded
    checkLabelText();
}

hideSecondaryBlock("label_tax_5", "tax_block_6");
hideSecondaryBlock("label_extra_1", "extra_block_2");
hideSecondaryBlock("label_tax_5", "extra_block_4");

function parseDate(labelText) {
    if (!labelText) return null;
    let parts = labelText.trim().split("-");
    if (parts.length !== 3) return null; // Invalid format check
    return new Date(parts[2], parts[1] - 1, parts[0]); // Convert to Date object (yyyy, mm-1, dd)
}

function compareDates(labelId1, labelId2, hiddenFieldId) {
    let label1 = document.getElementById(labelId1);
    let label2 = document.getElementById(labelId2);
    let hiddenField = document.getElementById(hiddenFieldId);

    if (!label1 || !label2 || !hiddenField) return; // Prevent errors if elements are missing

    let date1 = parseDate(label1.textContent);
    let date2 = parseDate(label2.textContent);

    if (!date1 || !date2) return; // Prevent errors if date parsing fails

    if (date1 > date2) {
        hiddenField.style.display = "none"; // Hide if label_date_1 is greater
    } else {
        hiddenField.style.display = "block"; // Show otherwise
    }
}

// Function to monitor changes in labels
function observeDateChanges(labelId1, labelId2, hiddenFieldId) {
    let observer = new MutationObserver(() => compareDates(labelId1, labelId2, hiddenFieldId));
    // Limit observation scope to childList only for better performance
    let observerOptions = { childList: true };

    let label1 = document.getElementById(labelId1);
    let label2 = document.getElementById(labelId2);
    if (label1) observer.observe(label1, observerOptions);
    if (label2) observer.observe(label2, observerOptions);

    compareDates(labelId1, labelId2, hiddenFieldId); // Initial check
}

// Compare both dates and only show the extra block if the user signed contracted in NL.
observeDateChanges("label_tax_2", "label_extra_0", "extra_block_1");


document.addEventListener("DOMContentLoaded", function () {
    if (document.body.id !== "results") return;

    // Check for empty/None values in required fields before submitting
    document.querySelector("form").addEventListener("submit", function (event) {
        let valid = true;

        document.querySelectorAll(".validate-required").forEach((input) => {
            const value = input.value.trim();
            const parentDiv = input.closest("div");

            const existingWarning = parentDiv.querySelector(".warning");
            if (existingWarning) existingWarning.remove();

            if (value === "" || value.toLowerCase() === "none") {
                valid = false;

                const warning = document.createElement("p");
                warning.textContent = "Dit veld mag niet leeg zijn!";
                warning.className = "warning text-red-500 mt-2 text-sm";
                parentDiv.appendChild(warning);
            }
        });

        // Prevent form submission if validation fails
        if (!valid) {
            event.preventDefault();
            alert("Je bent waarschijnlijk iets vergeten!");
        }
    });

    // Prevent <enter> from submitting form and make toggleEdit work with enter
    document.querySelectorAll('input[type="text"]').forEach((input) => {
        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                const [_, type, index] = this.id.split("_");
                toggleEdit(type, index);
            }
        });
    });

    // Handling form submission
    document.querySelector("form").addEventListener("submit", function (event) {
        document.querySelectorAll('input[type="text"]').forEach((input) => {
            const [_, type, index] = input.id.split("_");
            const label = document.getElementById(`label_${type}_${index}`);
            if (label) {
                label.textContent = input.value;
            }
        });
    });
});

/**
 * Creates a reusable function to add rows with inputs to a container
 * @param {Object} config - Configuration object with the following properties:
 * @param {string} config.buttonId - ID of the button that triggers adding rows
 * @param {string} config.containerId - ID of the container where rows will be added
 * @param {string} config.prefix - Prefix for data attributes and input names (e.g., 'tax', 'personal')
 * @param {Array} config.inputs - Array of input configurations
 * @param {boolean} config.addRemoveButton - Whether to add a remove button (default: true)
 * @param {boolean} config.addEditButton - Whether to add an edit button (default: true)
 * @param {string} config.editButtonText - Text for the edit button (default: 'wijzig')
 * @param {Function} config.onRowAdded - Callback function when a row is added (optional)
 */
function setupInputRowAdder(config) {
    const {
        buttonId, 
        containerId, 
        prefix,
        inputs,
        addRemoveButton = true,
        addEditButton = true,
        editButtonText = 'wijzig',
        onRowAdded = null
    } = config;
    
    document.getElementById(buttonId).addEventListener("click", function() {
        addInputRow(config);
    });
}

/**
 * Adds a new row of inputs based on the provided configuration
 * @param {Object} config - Same configuration object as setupInputRowAdder
 * @returns {HTMLElement} - The newly created row element
 */
function addInputRow(config) {
    const {
        containerId, 
        prefix,
        inputs,
        addRemoveButton = true,
        addEditButton = true,
        editButtonText = 'wijzig',
        onRowAdded = null
    } = config;
    
    const container = document.getElementById(containerId);
    const newIndex = container.children.length + 1;
    const newRow = document.createElement("div");
    
    newRow.classList.add("flex", "flex-wrap", "justify-evenly", "items-center", "border-b");
    newRow.id = `row_${prefix}_${newIndex}`;
    
    // Create inputs based on configuration
    let inputsHTML = '';
    inputs.forEach(input => {
        inputsHTML += `
            <div class="flex flex-col w-full md:w-1/${inputs.length <= 2 ? '2' : '4'}">
                <label data-label="${prefix}_${newIndex}"
                    class="p-3 w-full font-semibold break-words text-xl">
                </label>
                <input data-input="${prefix}_${newIndex}"
                    class="border border-gray-300 text-black text-xl p-3 w-full rounded-lg focus:outline-none hidden"
                    type="text" name="data_${prefix}_${input.fieldName}_${newIndex}" 
                    placeholder="${input.placeholder || ''}"
                    value="${input.defaultValue || ''}">
            </div>
        `;
    });
    
    // Create buttons section
    let buttonsHTML = '';
    if (addEditButton || addRemoveButton) {
        buttonsHTML = '<div class="flex justify-end w-full mt-2">';
        
        if (addEditButton) {
            buttonsHTML += `
                <!-- Edit Button -->
                <button type="button"
                    class="bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold py-3 px-4 m-2 rounded-lg shadow-md transition-all duration-300"
                    onclick="toggleEditInputs('${prefix}', ${newIndex})">
                    ${editButtonText}
                </button>
            `;
        }
        
        if (addRemoveButton) {
            buttonsHTML += `
                <!-- Remove Button -->
                <button type="button"
                    class="bg-red-600 hover:bg-red-700 text-white text-xl font-semibold py-3 px-4 m-2 rounded-lg shadow-md transition-all duration-300"
                    onclick="removeRow('row_${prefix}_${newIndex}')">
                    x
                </button>
            `;
        }
        
        buttonsHTML += '</div>';
    }
    
    // Combine everything
    newRow.innerHTML = inputsHTML + buttonsHTML;
    
    // Add the new row to the container
    container.appendChild(newRow);
    
    // Call the callback if provided
    if (onRowAdded && typeof onRowAdded === 'function') {
        onRowAdded(newRow, newIndex);
    }
    
    return newRow;
}

// Required supporting function for the remove button
function removeRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.remove();
    }
}

// Improved toggle function that works with any number of inputs
function toggleEditInputs(prefix, index) {
    const labels = document.querySelectorAll(`label[data-label^="${prefix}_${index}_"]`);
    const inputs = document.querySelectorAll(`input[data-input^="${prefix}_${index}_"]`);
    
    labels.forEach(label => {
        label.classList.toggle('hidden');
    });
    
    inputs.forEach(input => {
        input.classList.toggle('hidden');
        
        // Get the field name from the data-input attribute
        const fieldName = input.getAttribute('data-input').split('_')[2];
        
        if (!input.classList.contains('hidden')) {
            input.focus();
        } else {
            // Update corresponding label with input value when hiding input
            const correspondingLabel = document.querySelector(`label[data-label="${prefix}_${index}_${fieldName}"]`);
            if (correspondingLabel) {
                correspondingLabel.textContent = input.value || '';
            }
        }
    });
}

// Example usage for your specific scenarios:
document.addEventListener('DOMContentLoaded', function() {
    // Setup for two inputs per row
    setupInputRowAdder({
        buttonId: "addTwoInputRowButton",
        containerId: "nl_residence_dates_container",
        prefix: "tax",
        inputs: [
            { fieldName: "start_date", placeholder: "Start Date" },
            { fieldName: "end_date", placeholder: "End Date" }
        ],
        addEditButton: true,
        addRemoveButton: true
    });
    
    // Setup for four inputs per row
    setupInputRowAdder({
        buttonId: "addFourInputRowButton",
        containerId: "contact_info_container",
        prefix: "contact",
        inputs: [
            { fieldName: "name", placeholder: "Name" },
            { fieldName: "email", placeholder: "Email", defaultValue: "@example.com" },
            { fieldName: "phone", placeholder: "Phone Number" },
            { fieldName: "address", placeholder: "Address" }
        ],
        addEditButton: true,
        addRemoveButton: true,
        editButtonText: "Edit"
    });
    
    // You can add more configurations as needed
});