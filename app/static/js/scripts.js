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

// code for adding location rows
document.getElementById("addRowButton").addEventListener("click", function () {
    const container = document.getElementById("location-container");
    const newIndex = container.children.length + 1; // Unique index for the new row

    const newRow = document.createElement("div");
    newRow.classList.add("flex", "justify-evenly", "items-center");
    newRow.id = `row_${newIndex}`;

    newRow.innerHTML = `
                          <label data-label="tax_${newIndex}"
                        class="border border-white p-3 w-full font-semibold break-words text-xl">
                        
                      </label>
                      <input data-input="tax_${newIndex}"
                        class="border border-gray-300 text-black text-xl p-3 w-full rounded-lg focus:outline-none hidden"
                        type="text" name="start_date_${newIndex}" value="">

                      <label data-label="tax_${newIndex}"
                        class="border border-white p-3 w-full font-semibold break-words text-xl">
                        
                      </label>
                      <input data-input="tax_${newIndex}"
                        class="border border-gray-300 text-black text-xl p-3 w-full rounded-lg focus:outline-none hidden"
                        type="text" name="end_date_${newIndex}" value="">

                      <label data-label="tax_${newIndex}"
                        class="border border-white p-3 w-full font-semibold break-words text-xl">
                        
                      </label>
                      <input data-input="tax_${newIndex}"
                        class="border border-gray-300 text-black text-xl p-3 w-full rounded-lg focus:outline-none hidden"
                        type="text" name="city_${newIndex}" value="">

                      <label data-label="tax_${newIndex}"
                        class="border border-white p-3 w-full font-semibold break-words text-xl">
                        
                      </label>
                      
                      <input data-input="tax_${newIndex}"
                        class="border border-gray-300 text-black text-xl p-3 w-full rounded-lg focus:outline-none hidden"
                        type="text" name="country_${newIndex}" value="">
                   
                      <div class="flex justify-end w-full">
                      <!-- Edit Button -->
                      <button type="button"
                        class="bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold py-3 px-4 mx-2 rounded-lg shadow-md transition-all duration-300"
                        onclick="toggleEditLocation('tax', ${newIndex})">
                        wijzig
                      </button>

                      <!-- Remove Button -->
                      <button type="button"
                        class="bg-red-600 hover:bg-red-700 text-white text-xl font-semibold py-3 px-4 mx-2 rounded-lg shadow-md transition-all duration-300"
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
