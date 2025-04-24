(() => {
  // Add styling for the PubMed link if it hasn't already been added.
  if (!document.getElementById('pubmed-link-style')) {
    const style = document.createElement('style');
    style.id = 'pubmed-link-style';
    style.innerHTML = `
      .pubmed-link {
        text-decoration: underline;
        color: inherit;
        cursor: pointer;
      }
      .pubmed-link:hover {
        color: blue;
      }
    `;
    document.head.appendChild(style);
  }

  // Cache the modal element
  const paperModal = document.querySelector('.paper-overlay');
  const TEXT_SCALE_FACTOR = 47; // Adjust as needed
  const stopWords = ['the', 'and', 'of', 'a', 'an', 'in', 'on', 'for', 'to', 'with'];

  // If there's no .paper-overlay, we simply won't set up the rest
  if (!paperModal) {
    return;
  }

  // ---- Utility/Helper Functions ---- //

  function filterKeywords(title) {
    return title
      .split(/\s+/)
      .filter(word => word.length > 2 && !stopWords.includes(word.toLowerCase()));
  }

  function rescaleText() {
    const height = window.innerHeight,
          width = window.innerWidth;
    return Math.min(width / TEXT_SCALE_FACTOR, height / TEXT_SCALE_FACTOR);
  }

  function closeModal() {
    paperModal.style.display = 'none';
    paperModal.innerHTML = '';
  }

  function highlightKeywords(text, keywords) {
    let highlightedText = text;
    keywords.forEach(word => {
      const escapedWord = word.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
      const regex = new RegExp(`\\b${escapedWord}\\b`, 'gi');
      highlightedText = highlightedText.replace(regex, `<span style="color: red;">$&</span>`);
    });
    return highlightedText;
  }

  function cleanSnippet(rawText) {
    let cleaned = rawText;

    // Remove leading/trailing non-alphanumeric chars
    cleaned = cleaned.replace(/^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$/g, '');

    // Remove bracketed labels like "INTRO':", etc.
    cleaned = cleaned.replace(
      /^(?:(?:INTRO|RESULTS|DISCUSS|ABSTRACT)':\s*(?:(?:(?:\d+\.\s*)?')|(?:'(?:\d+\.\s*)?)|(?:\d+\.\s*)|)(Introduction|Background|Results|Discussion|Abstract)|(?:TITLEABSTRACT)':\s*')/i,
      ''
    );
    cleaned = cleaned.replace(
      /^(?:(?:INTRO|RESULTS|DISCUSS|ABSTRACT)':\s*(?:(?:\d+\.\s*)?'?)?(?:Introduction|Background|Results|Discussion|Abstract)|TITLEABSTRACT':\s*)/i,
      ''
    );
    // 1) remove newlines
    cleaned = cleaned.replace(/\r?\n/g, '');

    // 2) kill any stray "n." at the very end
    cleaned = cleaned.replace(/n\.$/, '.');

    // 3) ensure a trailing period
    if (!cleaned.endsWith('.')) {
      cleaned += '.';
    }
    cleaned = cleaned.trim();

    if (cleaned && !cleaned.endsWith('.')) {
      cleaned += '.';
    }

    return cleaned;
  }

  /**
   * Fetches snippet from your backend and article details from PubMed,
   * then displays them in a modal.
   */
  function addModalContent(p_source, source, typa, target) {
    const fontSize = rescaleText();

    // Show a loading message.
    paperModal.innerHTML = `
      <div class="modal-content" style="font-size: ${fontSize}px;">
        <h5>Fetching content...</h5>
      </div>
    `;
    paperModal.style.display = "block";
    paperModal.style.zIndex = "9999";

    // 1. Fetch snippet from your own endpoint
    const snippetPromise = fetch('/process-text-withoutapi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_source: p_source })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Snippet API call unsuccessful.');
      }
      return response.json();
    });

    // 2. Fetch paper details from PubMed EFetch
    const pubmedPromise = fetch(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=${p_source}&retmode=xml`)
    .then(response => {
      if (!response.ok) {
        throw new Error('PubMed EFetch API call unsuccessful.');
      }
      return response.text();
    })
    .then(xmlString => {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(xmlString, 'text/xml');
      const articleTitleElem = xmlDoc.querySelector('ArticleTitle');
      const pubmedTitle = articleTitleElem ? articleTitleElem.textContent : 'Title not available.';
      const authorsNodes = xmlDoc.querySelectorAll('Author');
      let authorsArray = [];
      authorsNodes.forEach(author => {
        const collectiveNameElem = author.querySelector('CollectiveName');
        if (collectiveNameElem) {
          authorsArray.push(collectiveNameElem.textContent);
        } else {
          const lastNameElem = author.querySelector('LastName');
          const foreNameElem = author.querySelector('ForeName');
          if (lastNameElem && foreNameElem) {
            authorsArray.push(`${foreNameElem.textContent} ${lastNameElem.textContent}`);
          }
        }
      });
      const pubmedAuthors = authorsArray.length > 0 ? authorsArray.join(', ') : 'Authors not available.';
      return { pubmedTitle, pubmedAuthors };
    });

    // Wait for both fetches
    Promise.all([snippetPromise, pubmedPromise])
      .then(([snippetData, pubmedDetails]) => {
        let text_input = snippetData.text_input || 'No content returned.';
        text_input = cleanSnippet(text_input);

        // Build the title from any defined parts
        const titleParts = [source, typa, target].filter(part => part && part !== "undefined");
        const titleString = titleParts.length > 0 ? titleParts.join(' ') : `Publication ${p_source}`;

        // Extract keywords from the title
        const keywords = filterKeywords(titleString);
        // Highlight them in the snippet
        const highlightedText = highlightKeywords(text_input, keywords);

        // Build the modal content
        const contents = `
          <div class="modal-content" style="font-size: ${fontSize}px;">
              ${titleString ? `<h4>${titleString}</h4><br>` : ''}
              <p><strong>PubMed Title:</strong> ${pubmedDetails.pubmedTitle}</p>
              <p><strong>Authors:</strong> ${pubmedDetails.pubmedAuthors}</p>
              <br>
              <p>
                <a href="https://pubmed.ncbi.nlm.nih.gov/${p_source}" target="_blank" class="pubmed-link">
                  Click here
                </a> to view publication.
              </p>
              <br>
              <p><strong>Respective text from publication:</strong> ${highlightedText}</p>
          </div>
        `;
        paperModal.innerHTML = contents;
      })
      .catch(error => {
        console.error(`Error while fetching data / rendering modal: ${error.message}`);
        paperModal.innerHTML = `
          <div class="modal-content" style="font-size: ${fontSize}px;">
            <h5>Error loading content.</h5>
          </div>
        `;
      });
  }

  // Close modal by clicking outside
  paperModal.addEventListener('click', (event) => {
    if (event.target === paperModal) {
      closeModal();
    }
  });

  // Attach event listeners to .pubmed-link elements
  const pubmedLinks = document.querySelectorAll('span.pubmed-link');
  pubmedLinks.forEach(link => {
    const p_source = link.getAttribute('data-p_source');
    const source   = link.getAttribute('data-source');
    const typa     = link.getAttribute('data-typa');
    const target   = link.getAttribute('data-target');
    link.addEventListener('click', () => addModalContent(p_source, source, typa, target));
  });

  // Expose addModalContent globally if needed
  window.addModalContent = addModalContent;
})();