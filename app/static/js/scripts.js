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
