/*
This file contains the original JavaScript contained inside gene.html (the <script> tags),
but reworked to avoid "Cannot read properties of null (reading 'addEventListener')"
by carefully checking for elements and/or using DOMContentLoaded.
*/

// -------------- Utility Functions -------------- //

// Recalculate layout function (unchanged logic, just placed at top level)
function recalculateLayout() {
  const cy = document.getElementById("cy")._cyreg.cy;

  // Get visible nodes and edges
  const visibleNodes = cy.nodes(":visible").filter(node => node.degree() > 0); // Exclude disconnected nodes
  const visibleEdges = cy.edges(":visible");
  const visibleElements = visibleNodes.union(visibleEdges);

  const numNodes = visibleNodes.length;
  console.log(`Recalculating layout for ${numNodes} visible nodes...`);

  let layout;
  if (numNodes < 1000) {
    console.log('Applying COSE layout...');
    layout = visibleElements.layout({
      name: "cose",
      animate: true,
      refresh: 4,
      fit: true,
      padding: 30,
      boundingBox: undefined,
      randomize: true,
      debug: false,
      nodeRepulsion: 200000,
      nodeOverlap: 10,
      idealEdgeLength: 10,
      edgeElasticity: 100,
      nestingFactor: 5,
      gravity: 250,
      numIter: 100,
      initialTemp: 200,
      coolingFactor: 0.95,
      minTemp: 1.0
    });
  } else {
    console.log('Applying FCOSE layout...');
    layout = visibleElements.layout({
      name: 'fcose',
      quality: 'proof',
      randomize: true,
      animate: false,
      fit: true,
      padding: 30,
      nodeRepulsion: 10000,
      edgeElasticity: 0.5,
      nestingFactor: 0.1,
      gravityRangeCompound: 2.0,
      gravity: 0.1,
      minNodeSpacing: 50,
      nodeDimensionsIncludeLabels: true
    });
  }

  layout.run(); // Apply the selected layout
}

// Helper to decode HTML entities (unchanged)
function decodeHTMLEntities(text) {
  var textArea = document.createElement("textarea");
  textArea.innerHTML = text;
  return textArea.value;
}

// Convert the global `g` string into a JSON array and export it as TSV
function downloadTableAsTSV(filename) {
  // 1) Header row
  let tsvContent =
    "Resolved Source\tResolved Source Type\tResolved Relationship\tResolved Target\tResolved Target Type\tSection\tPubmed ID\tSpecies\tBasis\tSource_extracted_definition\tSource_generated_definition\tTarget_extracted_definition\tTarget_generated_definition\tOriginal Source\tOriginal Source Type\tOriginal Target\tOriginal Target Type\tOriginal Relationship\n";

  // 2) Turn your HTML‑escaped JSON string into valid JSON
  let decoded = decodeHTMLEntities(g)
    // replace single‑quoted keys with double‑quoted
    .replace(
      /'(\b(?:id|idtype|target|targettype|edge_disamb|publication|p_source|species|basis|source_extracted_definition|source_generated_definition|target_extracted_definition|target_generated_definition|entity1|entity2|entity1type|entity2type|inter_type)\b)':/g,
      '"$1":'
    )
    .replace(/\bNone\b/g, '"None"')
    // replace single‑quoted string values with double‑quoted
    .replace(/:\s*'([^']+)'/g, (_m, v) => `: "${v.replace(/"/g, '\\"')}"`);

  console.log(decoded);
  const g_list = JSON.parse(decoded);

  // 3) Build TSV rows
  g_list.forEach(item => {
    tsvContent += [
      item.id,
      item.idtype,
      item.edge_disamb,
      item.target,
      item.targettype,
      item.p_source.toUpperCase(),
      item.publication,
      item.species,
      item.basis,
      item.source_extracted_definition,
      item.source_generated_definition,
      item.target_extracted_definition,
      item.target_generated_definition,
      item.entity1,
      item.entity1type,
      item.entity2,
      item.entity2type,
      item.inter_type
    ].join("\t") + "\n";
  });

  // 4) Trigger download
  const blob = new Blob([tsvContent], { type: "text/tab-separated-values" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

// Export the current Cytoscape visualization as an SVG
function downloadAsSVG() {
  // Assuming your Cytoscape instance is named 'cy'
  const cy = document.getElementById("cy")._cyreg.cy;

  // Register the SVG Exporter plugin
  cytoscape.use(cytoscapeSvg);

  // Export the network view as an SVG
  const svgContent = cy.svg({ copyStyles: true, bg: "white" });

  // Modify the downloaded SVG to have black letters
  const svgDOM = new DOMParser().parseFromString(svgContent, "image/svg+xml");
  const labels = svgDOM.querySelectorAll("text");
  labels.forEach((label) => label.setAttribute("fill", "#000000"));
  const modifiedSvgContent = new XMLSerializer().serializeToString(svgDOM);

  // Create a Blob from the SVG content
  const blob = new Blob([modifiedSvgContent], {
    type: "image/svg+xml;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);

  // Create a link element, set its href to the Blob URL, and trigger download
  const link = document.createElement("a");
  link.href = url;
  link.download = "network.svg";
  link.click();

  // Revoke the Blob URL
  URL.revokeObjectURL(url);
}

// A helper for sorting tables
function sortTable(table, column, asc = true) {
  const directionModifier = asc ? 1 : -1;
  const rows = Array.from(table.tBodies[0].querySelectorAll("tr"));

  const sortedRows = rows.sort((a, b) => {
    const aColText = a
      .querySelector(`td:nth-child(${column + 1})`)
      .textContent.trim();
    const bColText = b
      .querySelector(`td:nth-child(${column + 1})`)
      .textContent.trim();

    return aColText.localeCompare(bColText) * directionModifier;
  });

  while (table.tBodies[0].firstChild) {
    table.tBodies[0].removeChild(table.tBodies[0].firstChild);
  }
  table.tBodies[0].append(...sortedRows);

  table.setAttribute("data-sort-direction", asc ? "asc" : "desc");
  table.setAttribute("data-sort-column", column);
}

// ---------------- MAIN DOMContentLoaded SECTION ---------------- //
document.addEventListener("DOMContentLoaded", () => {
  // 1. Search form for node-search-form
  const searchForm = document.getElementById("node-search-form");
  if (searchForm) {
    searchForm.addEventListener("submit", function (event) {
      event.preventDefault();
      const searchTerm = event.target[0].value.toLowerCase();
      const cy = document.getElementById("cy")._cyreg.cy;
      const matchingNodes = cy.nodes().filter(function (node) {
        const nodeId = node.id().toLowerCase();
        if (nodeId === searchTerm) {
          return true;
        }
        return nodeId.includes(searchTerm);
      });
      cy.nodes().style("opacity", "0.5");
      matchingNodes.style("opacity", "1");
    });
  }

  // 2. Download button for "download-pdf" (SVG export)
  const pdfButton = document.getElementById("download-pdf");
  if (pdfButton) {
    pdfButton.addEventListener("click", downloadAsSVG);
  }

  // 3. Sorting table code for .sortable thead th
  const sortableHeaders = document.querySelectorAll(".sortable thead th");
  if (sortableHeaders.length > 0) {
    sortableHeaders.forEach((headerCell) => {
      headerCell.addEventListener("click", () => {
        const table = headerCell.closest("table");
        if (!table) return;
        const columnIndex = Array.from(headerCell.parentElement.children).indexOf(headerCell);
        const currentDirection = table.getAttribute("data-sort-direction") === "asc";
        sortTable(table, columnIndex, !currentDirection);
      });
    });
  }

  // 4. Resize #cy_wrapper to 80% of window height after window loads
  $(window).on("load", function () {
    const cyWrapper = document.getElementById("cy_wrapper");
    if (cyWrapper) {
      cyWrapper.style.height = `${window.innerHeight * 0.8}px`;
    }
  });
});