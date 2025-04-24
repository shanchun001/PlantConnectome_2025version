const results_container = document.querySelector('#body_results');              // Where the elements to paginate are
const results = (function() {
    let data = [];
    results_container.childNodes.forEach(node => {
        let text_data = node.textContent.trim().replaceAll("\n", "");
        if (text_data.length) {
            data.push(text_data.split('  ').filter(term => term.length).map(term => term.trim()))
        } 
    })
    return data;
})();                                                                           // Stuff that we want to paginate
const pagination_numbers = document.querySelector('.pagination.text-center');   // Container for pagination numbers
const items_per_page = 50;                                                      // Display 50 items per pagination
const items_to_show = Math.ceil(results.length / items_per_page);               // Determines how many pagination numbers are needed
var pagination_number_arrays = [];                                            // Contains the pagination numbers to be used
var current_page = 1, back_button = '', forward_button = '';


// Add the pagination numbers when the page loads:
const add_pagination_elements = () => {
    let start = document.createElement('li'), finish = document.createElement('li');
    finish.setAttribute('onclick', 'go_next()');
    let finish_text = document.createElement('a');

    start.setAttribute('class', 'pagination-previous disabled') ; finish.setAttribute('class', 'pagination-next');
    finish_text.innerText = 'Next';
    start.innerText = 'Previous' ; finish.appendChild(finish_text);
    pagination_number_arrays.push(start) ; pagination_number_arrays.push(finish);

    back_button = start; forward_button = finish;

    for (let i = items_to_show ; i >= 1 ; i--) {
        let element = document.createElement('li'), number = document.createElement('a')
        number.setAttribute('aria-label', `Page ${i}`);
        number.innerText = i;
        element.setAttribute('onclick', `display_items(${i})`);
        if (i === 1) {
            number.setAttribute('class', 'current');
        }
        element.appendChild(number);

        pagination_number_arrays.splice(1, 0, element);
    }
    
    pagination_number_arrays.forEach(number => {
        pagination_numbers.appendChild(number);
    })
}

const toggle_back_forward = () => {
    /* 
    Toggles the appearance of the previous buttons.
    */
    if (current_page === 1 && back_button.querySelector('a')) {
        back_button.children = [];
        back_button.innerText = 'Previous';
        back_button.classList.add('disabled');
        back_button.removeAttribute('onclick')
    } else if (current_page === items_to_show && forward_button.querySelector('a')) {
        forward_button.innerText = 'Next';
        forward_button.classList.add('disabled');
        forward_button.children = [];
        forward_button.removeAttribute('onclick');
    }

    if (!back_button.querySelector('a') && current_page > 1) {
        let elem = document.createElement('a');
        elem.innerText = 'Previous';
        back_button.innerText = '';
        back_button.classList.remove('disabled');
        back_button.appendChild(elem);
        back_button.setAttribute('onclick', `go_back()`)
    } else if (!forward_button.querySelector('a') && current_page < items_to_show) {
        let elem = document.createElement('a');
        elem.innerText = 'Next';
        forward_button.innerText = '';
        forward_button.classList.remove('disabled');
        forward_button.appendChild(elem);
        forward_button.setAttribute('onclick', `go_next()`);
    }
}

// END

const show_active_elements = (p) => {
    /*
    Toggles the appearance of the page numbers.
    */
    current_page = p ; toggle_back_forward()
    const paginations = document.querySelector('.pagination.text-center').querySelectorAll('li');
    Array.from(paginations).slice(1, paginations.length - 1).forEach(number => {
        let current = number.innerText;
        if (current === p.toString()) {
            number.setAttribute('class', 'current');
            let original = number.querySelector('a');
            number.innerText = original.innerText;
            number.removeAttribute('onclick');
            number.children = [];
        }

        if (current !== p.toString()) {
            number.setAttribute('class', '');
            if (!number.querySelector('a')) {
                let n = number.innerText, elem = document.createElement('a');
                elem.innerText = n;
                number.innerText = '';
                number.setAttribute('onclick', `display_items(${n})`);
                number.appendChild(elem);
            }
        }
    })
}

const go_back = () => {
    current_page--;
    display_items(current_page);
}

const go_next = () => {
    current_page++;
    display_items(current_page);
}

// Displaying the active elements by the pagination element:
const display_items = (page_number) => {
    /*
    Displays items based on which pagination number is clicked.
    */
    let lower = (page_number - 1) * items_per_page, higher = items_per_page * page_number;
    show_active_elements(page_number)

    results_container.innerHTML = '';
    results.forEach((item, index) => {
        if (index < higher && index >= lower) {
            results_container.innerHTML += `<tr>` + 
            `<td> ${item[0]} </td>` + 
            `<td> ${item[1]} </td>` + 
            `<td> ${item[2]} </td>` + 
            `<td> ${item[4].toLowerCase()} </td>` + 
            `<td class = 'pubmed-link pubmed-hyperlink' data-pubmed-id = '${item[3]}' data-source = '${item[0]}'
            data-typa = '${item[1]}' data-target = '${item[2]}' onclick = "addModalContent('${item[3]}', '${item[0]}', '${item[1]}', '${item[2]}')"> ${item[3]} </td>` + 
            `</tr>`;
        }
    })
}

// END

window.addEventListener('load', () => {
    add_pagination_elements();
    display_items(1);
});