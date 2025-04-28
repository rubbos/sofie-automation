// Function to copy the text of a report to the clipboard
function copyReport(reportId) {
    const content = document.getElementById(reportId).innerText;

    navigator.clipboard.writeText(content)
        .then(() => {
            alert('Report copied to clipboard!');
        })
        .catch(err => {
            console.error('Failed to copy: ', err);
        });
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