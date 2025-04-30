// Get forms in order of gene-form, name-form, and title-form:
const forms = document.querySelectorAll('form');

const titleInput = document.getElementById("gene_id");

// Change placeholder text based on which button is being hovered over.
const setupButtonHoverEvents = () => {
    const buttonConfigs = [
        { value: 'Word', placeholder: "e.g., CESA (hit 'Enter' to search)", defaultPlaceholder: "e.g., CESA (hit 'Enter' to search)" },
        { value: 'Exact', placeholder: "e.g., CESA (hit 'Enter' to search)", defaultPlaceholder: "e.g., CESA (hit 'Enter' to search)" },
        { value: 'Alias', placeholder: "e.g., CESA1 (hit 'Enter' to search)", defaultPlaceholder: "e.g., CESA1 (hit 'Enter' to search)" },
        { value: 'Substring', placeholder: "e.g., CESA (hit 'Enter' to search)", defaultPlaceholder: "e.g., CESA (hit 'Enter' to search)" },
        { value: 'Non-alphanumeric', placeholder: "e.g., CESA1 (hit 'Enter' to search)", defaultPlaceholder: "e.g., CESA1 (hit 'Enter' to search)" },
        { value: 'Paired-entity', placeholder: "e.g., hair$pollen (hit 'Enter' to search)", defaultPlaceholder: "e.g., hair$pollen (hit 'Enter' to search)" }
    ];

    buttonConfigs.forEach(config => {
        let button = document.querySelector(`input[value = ${config.value}]`);
        if (button) {
            button.addEventListener('mouseover', () => {
                titleInput.placeholder = config.placeholder;
            });
            button.addEventListener('mouseout', () => {
                titleInput.placeholder = config.defaultPlaceholder;
            });
        }
    });
}

// Attaches event listeners to the gene form.
const gene_form_listeners = () => {
    let form_buttons = forms[0].querySelectorAll('.button');
    let form_actions = (function() {
        let temp = [];
        form_buttons.forEach(button => {
            temp.push(button.getAttribute('formaction'));
        })
        return temp;
    })();
    
    for (let i = 0 ; i < form_buttons.length ; i++) {
        form_buttons[i].addEventListener('click', () => {
            submitGeneForm(event, forms[0], form_actions[i]);
        });
    }
}
// assume forms[1] is your author form, forms[2] your title form
const authorForm = forms[1];
const titleForm  = forms[2];

// 1️⃣ Bind author default
authorForm.addEventListener('submit', e => {
  const input = document.getElementById('author');
  if (!input.value.trim()) {
    input.value = 'Mutwil M';
  }
  // let the browser proceed with submission
});

// 2️⃣ Bind PubMed ID default
titleForm.addEventListener('submit', e => {
  const input = document.getElementById('title');
  if (!input.value.trim()) {
    input.value = '38050352';
  }
  // let the browser proceed with submission
});
// Methods for submitting the gene form via buttons:
// Function to show the loading icon and background overlay
function showLoading() {
    //document.getElementById('loading-icon').style.display = 'inline-block'; // Show the main loading icon
    document.getElementById('loading-text').style.display = 'inline-block';    
    document.getElementById('loading-icon-small').style.display = 'inline-block'; // Show the small loading icon
}

// Function to hide the loading icon and background overlay
function hideLoading() {
    const icon = document.getElementById('loading-icon');
    const text = document.getElementById('loading-text');
    const smallIcon = document.getElementById('loading-icon-small');

    if (icon) icon.style.display = 'none';
    if (text) text.style.display = 'none';
    if (smallIcon) smallIcon.style.display = 'none';
}

// Attach the showLoading function to the form submission buttons
document.querySelectorAll('form .button').forEach(button => {
    button.addEventListener('click', showLoading);
});

function submitGeneForm(event, form, path) {
    event.preventDefault(); // Prevent form submission initially

    // Default title values for different paths
    const defaultTitles = {
        '/form/gene_id/alias': 'CESA1',
        '/form/gene_id/exact': 'CESA',
        '/form/gene_id/normal': 'CESA',
        '/form/gene_id/substring': 'CESA',
        '/form/gene_id/paired_entity': 'hair$pollen',
        '/form/gene_id/non_alpha': 'CESA1'
    };

    let inputVal = titleInput.value.trim();

    // If input is empty, set to default based on path
    if (inputVal.length === 0) {
        titleInput.value = defaultTitles[path] || '';
        inputVal = titleInput.value;
    }

    // If input is still less than 3 characters, block submission
    if (inputVal.length < 3) {
        alert("Please enter at least 3 characters to search.");
        return;
    }
    form.setAttribute('action', path);
    form.submit(); // Safe to submit
}



function submitFormWith(event, value) {
    event.preventDefault();
    // Submit the form with the clicked value
    const link = event.target;
    const form = link.closest('form');
    const input = form.querySelector('input[type="text"]');
    input.value = value;
    form.submit();
}

window.addEventListener('load', () => {
    setupButtonHoverEvents();
    gene_form_listeners();
    hideLoading();
    forms[1].setAttribute('onsubmit', `submitNameForm(event, forms[1])`);
    forms[2].setAttribute('onsubmit', `submitTitleForm(event, forms[2])`);
});

const loadingText = document.getElementById('loading-text');
loadingText.innerText = ''; // Clear the existing text

const words = "Loading in progress...".split(''); // Split into characters including spaces
let index = 0;

function typeEffect() {
    if (index < words.length) {
        if (words[index] === ' ') {
            loadingText.innerHTML += '&nbsp;'; // Add a non-breaking space
        } else {
            loadingText.innerText += words[index];
        }
        index++;
        setTimeout(typeEffect, 85); // Adjust speed of typing here
    } else {
        setTimeout(() => {
            loadingText.innerText = ''; // Clear text and restart typing effect
            index = 0;
            typeEffect();
        }, 1000); // Pause before restarting the typing effect
    }
}

typeEffect();


/*
This part of the file contains JavaScript for the help part of the landing page.
*/

// Selects the necessary HTML elements to change / attach event listeners to:
const help_information = document.querySelector('#help-text');
const help_buttons = document.querySelectorAll('.button-group')[1].querySelectorAll('.button');

// Change help information depending on which button is clicked:
const change_help_text = (button, text) => {
    /*
    Alters the appearance of the help button and the help text.
    */
    help_buttons.forEach(b => {
        if (b.innerText.toLowerCase() === text) {
            b.classList.remove('hollow');
        } else {
            b.classList.add('hollow');
        }
    })

    switch (text) {
        case 'gene / word':
            help_text = `
              <p>
                Find all entities where your query appears as a <em>standalone</em> word, 
                even if it contains hyphens or other non‑alphanumeric characters.
                For instance, if "CESA" is searched, the following entities will be identified:
              </p>
              <ul style="color: green;">
                <li>CESA</code></li>
                <li>Primary wall CESA-complex</code> (hyphenated)</li>
                <li>CesA/CSL superfamily</code> (slash‑delimited)</li>
                <li>CESA genes</li>
              </ul>
              <p>However, it will not find entities such as:</p>
              <ul style="color: red;">
                <li>CESA3</code> (contains alphanumericals in the same word)</li>
                <li>ATCESA</code> (embedded in a larger word)</li>
              </ul>
              <p>
      
            <p>You can search for <em>Arabidopsis thaliana</em> genes by entering an AGI number or an alias. For example, 'CESA1' would return:</p>
            <ul style="color: green;">
              <li>(ATCESA1, CESA1, RSW1, AT4G32410, ANY1)</li>
              <li>(ATCESA1, CESA1, RSW1, AT4G32410, ANY1) mutant</li>
            </ul>
          `;
          break;
        case 'exact':
            help_text = `
            <p>
                Finds the entity that <b>exactly</b> matches the search query. For instance, if "CESA4" is searched, the following entity will be found:
                <ul style = 'color: green;'>
                    <li> CESA4 </li>
                </ul>
                However, it will not find entities such as:
                <br> <br>
                <ul style = 'color: red;'>
                    <li> CESA4 genes </li>
                    <li> CESA </li>
                </ul>
            </p>`;
            break;
        case 'alias':
            help_text = `
            <p>
                Finds <b>all gene aliases</b> that are associated with the search query.  For instance, if "CESA1" is searched, this search will find the 
                following entities:
                <ul style = 'color: green;'>
                    <li> AT4G32410 </li>
                    <li> ANY1 </li>
                    <li> ATCESA1 </li>
                    <li> CESA1 </li>
                    <li> RSW1 </li>
                </ul>
            </p>`;
            break;
        case 'substring':
            help_text = `
            <p>
                Finds all entities that contain the search query. For instance, if "hair" is searched, this search will find the 
                following entities:
                <ul style = 'color: green;'>
                    <li> root hair </li>
                    <li> root hairs </li>
                    <li> hairy roots </li>

                </ul>
            </p>`;
            break;
        case 'non-alphanumeric':
            help_text = `
            <p>
                Finds all entities that contain the search query <b>followed by a non-alphanumeric character</b> (eg. "/", "-").  For instance, if "CESA1" 
                is searched, this search will find the following entities:
                <ul style = 'color: green;'>
                    <li> CESA1-3 </li>
                    <li> CESA1/3 </li>
                </ul>
                However, it will not find entities such as:
                <br> <br>
                <ul style = 'color: red;'>
                    <li> CESA10 </li>
                    <li> CESA10/3 </li>
                </ul>
            </p>`;   
            break;
        case 'paired-entity':
                help_text = `
                <p>
                    Finds all <b>paired entities</b> matches the search query split by "$".  For instance, if "hair$pollen" 
                    is searched, this search will find the following source and target pair entities:
                    <ul style = 'color: green;'>
                        <li> source node which contains: hair; target node which contains: pollen </li>
                        <li> source node which contains: pollen; target node which contains: hair </li>
                    </ul>
                    However, it will not find source and target pair entities such as:
                    <br> <br>
                    <ul style = 'color: red;'>
                        <li> source node which contains: hair; target node which contains: leaf </li>
                    </ul>
                </p>`;            
            break;
        default:
            help_text = `
            <p>
                Click one of the above buttons to find out more about each search function!
            </p>`;
            break;
    };
    help_information.innerHTML = help_text;
}

// Attach event listeners to each button:
help_buttons.forEach(button => {
    let button_text = button.innerText.toLowerCase();
    button.setAttribute('onclick', `change_help_text('${button}', '${button_text}')`);
    help_buttons[0].click();
})
