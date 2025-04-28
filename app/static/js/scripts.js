// Function to copy formatted report text to clipboard
function copyFormattedReport(reportId, notificationId) {
    const reportElement = document.getElementById(reportId);
    const notificationElement = document.getElementById(notificationId);

    if (navigator.clipboard && navigator.clipboard.write) {
        try {
            const htmlContent = reportElement.innerHTML;
            const textContent = reportElement.innerText;
            const htmlBlob = new Blob([htmlContent], { type: 'text/html' });
            const textBlob = new Blob([textContent], { type: 'text/plain' });
            const clipboardItem = new ClipboardItem({
                'text/html': htmlBlob,
                'text/plain': textBlob
            });

            navigator.clipboard.write([clipboardItem])
                .then(() => {
                    // Show notification after successful copy using Tailwind class
                    notificationElement.classList.remove('hidden');

                    // Hide the notification after 3 seconds
                    setTimeout(() => {
                        notificationElement.classList.add('hidden');
                    }, 3000);
                })
                .catch(err => {
                    console.log('Clipboard API failed, falling back to selection method', err);
                });
        } catch (err) {
            console.log('Error with Clipboard API, falling back', err);
        }
    }
}

// Residences
setupEntryManager({
    addButtonId: 'add-residence',
    entriesContainerId: 'residence-entries',
    templateId: 'residence-template',
    fieldNamePrefix: 'places_of_residence',
    minEntries: 1
});

// NL Residences dates
setupEntryManager({
    addButtonId: 'add-nl-residence-dates',
    entriesContainerId: 'nl-residence-dates-entries',
    templateId: 'nl-residence-dates-template',
    fieldNamePrefix: 'nl_residence_dates',
    minEntries: 0
});

// NL Private dates
setupEntryManager({
    addButtonId: 'add-nl-private-dates',
    entriesContainerId: 'nl-private-dates-entries',
    templateId: 'nl-private-dates-template',
    fieldNamePrefix: 'nl_private_dates',
    minEntries: 0
});
// NL Worked dates
setupEntryManager({
    addButtonId: 'add-nl-worked-dates',
    entriesContainerId: 'nl-worked-dates-entries',
    templateId: 'nl-worked-dates-template',
    fieldNamePrefix: 'nl_worked_dates',
    minEntries: 0
});
// NL dutch employer dates
setupEntryManager({
    addButtonId: 'add-nl-dutch-employer-dates',
    entriesContainerId: 'nl-dutch-employer-dates-entries',
    templateId: 'nl-dutch-employer-dates-template',
    fieldNamePrefix: 'nl_dutch_employer_dates',
    minEntries: 0
});

// Generic function to add entries to input fields
function setupEntryManager(options) {
    const {
        addButtonId,        // ID of the add button
        entriesContainerId, // ID of the container for all entries
        templateId,         // ID of the template
        fieldNamePrefix,    // Prefix for the field names (e.g., 'places_of_residence')
        minEntries = 1      // Minimum number of entries required
    } = options;

    // Add entry button
    document.getElementById(addButtonId).addEventListener('click', function () {
        const entryCount = document.querySelectorAll(`#${entriesContainerId} > div`).length;
        const template = document.getElementById(templateId).innerHTML;
        const newEntry = template.replace(/-_-/g, '-' + entryCount + '-');
        const entriesContainer = document.getElementById(entriesContainerId);
        entriesContainer.insertAdjacentHTML('beforeend', newEntry);
        setupRemoveButtons();
    });

    // Setup remove buttons
    function setupRemoveButtons() {
        document.querySelectorAll(`#${entriesContainerId} .remove-entry`).forEach(button => {
            button.removeEventListener('click', removeEntry);
            button.addEventListener('click', removeEntry);
        });
    }

    // Remove entry function
    function removeEntry() {
        const entriesContainer = document.getElementById(entriesContainerId);
        if (entriesContainer.children.length > minEntries) {
            this.closest(`#${entriesContainerId} > div`).remove();
            const entries = entriesContainer.children;
            for (let i = 0; i < entries.length; i++) {
                const inputs = entries[i].querySelectorAll('input, select');
                inputs.forEach(input => {
                    const name = input.getAttribute('name');
                    const newName = name.replace(new RegExp(`${fieldNamePrefix}-\\d+-`), `${fieldNamePrefix}-${i}-`);
                    input.setAttribute('name', newName);
                });
            }
        } else {
            const inputs = this.closest(`#${entriesContainerId} > div`).querySelectorAll('input, select');
            inputs.forEach(input => {
                input.value = '';
            });
        }
    }
    setupRemoveButtons();
}