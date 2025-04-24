  /**
   * Global constants and data preparation
   */
  const NODES_TO_RENDER = prepareNodes(_INSERT_NODES_HERE_);
  const EDGES_TO_RENDER = prepareEdges(_INSERT_EDGES_HERE_);
  function splitOutsideParentheses(input) {
    const result = [];
    let buffer = '';
    let parenDepth = 0;
    let bracketDepth = 0;
  
    for (let char of input) {
      if (char === '(') {
        parenDepth++;
        buffer += char;
      } else if (char === ')') {
        parenDepth--;
        buffer += char;
      } else if (char === '[') {
        bracketDepth++;
        buffer += char;
      } else if (char === ']') {
        bracketDepth--;
        buffer += char;
      } else if (char === ',' && parenDepth === 0 && bracketDepth === 0) {
        result.push(buffer.trim().toUpperCase());
        buffer = '';
      } else {
        buffer += char;
      }
    }
  
    if (buffer) {
      result.push(buffer.trim().toUpperCase());
    }
  
    return result;
  }
  var queryTerm = splitOutsideParentheses(queryTerms);
  //var queryTerm = queryTerms.split(',').map(term => term.trim().toUpperCase()); // Split, trim, and uppercase the query terms

  /**
   * Utility functions to prepare nodes and edges
   */
  function prepareNodes(nodes) {
    return [_INSERT_NODES_HERE_].map(node => ({
      ...node,
      data: {
        ...node.data,
        originalId: node.data.id, // disambiguated nodes
        id: (node.data.id + ' [' + node.data.type + ']').toUpperCase(), // Normalize ID to uppercase
        type: node.data.type,
        originalId_beforedisamb: node.data.originalid,
        type_beforedisamb: node.data.originaltype

      },
    }));
  }

  function prepareEdges(edges) {
    return [_INSERT_EDGES_HERE_].map(edge => ({
      ...edge,
      data: {
        ...edge.data,
        source: (edge.data.source + ' [' + edge.data.sourcetype + ']').toUpperCase(), // with2 are disambiguated sources
        originalsource: edge.data.source,
        sourcetype: edge.data.sourcetype,
        target: (edge.data.target + ' [' + edge.data.targettype + ']').toUpperCase(), 
        originaltarget: edge.data.target,
        targettype: edge.data.targettype,
        interaction: edge.data.interaction,
        source2: (edge.data.source2 + ' [' + edge.data.sourcetype2 + ']').toUpperCase(), // with2 are original sources
        originalsource2: edge.data.source2,
        sourcetype2: edge.data.sourcetype2,
        target2: (edge.data.target2 + ' [' + edge.data.targettype2 + ']').toUpperCase(), 
        originaltarget2: edge.data.target2,
        targettype2: edge.data.targettype2,
        interaction2: edge.data.interaction2,
        p_source: edge.data.p_source,
        pmid: edge.data.pmid,
        species: edge.data.species,
        basis: edge.data.basis,
        source_extracted_definition: edge.data.source_extracted_definition,
        source_generated_definition: edge.data.source_generated_definition,
        target_extracted_definition: edge.data.target_extracted_definition,
        target_generated_definition: edge.data.target_generated_definition
      },
    }));
  }

  // After preparing nodes and before rendering the graph:
  const validNodeIds = new Set(NODES_TO_RENDER.map(node => node.data.id));
  //console.log(validNodeIds);
  // Filter edges: keep only edges where both source and target exist in validNodeIds
  const filteredEdges = EDGES_TO_RENDER.filter(edge =>
    validNodeIds.has(edge.data.source) && validNodeIds.has(edge.data.target)
  );

  // Filter nodes: remove orphan nodes
  const edgeNodeIds = new Set();
  filteredEdges.forEach(edge => {
    edgeNodeIds.add(edge.data.source);
    edgeNodeIds.add(edge.data.target);
  });

  const filteredNodes = NODES_TO_RENDER.filter(node => edgeNodeIds.has(node.data.id));

  /**
   * Categorization map for node types
   */
  const categoryMap = {
    'biological process': [
      'metabolic pathway', 'function', 'pathway', 'signaling pathway',
      'metabolic process', 'cell process', 'biochemical process', 'cellular process',
      'molecular function', 'signalling pathway', 'genetic process', 'biological pathway', 'process'
    ],
    'cell/organ/organism': [
      'organism', 'organ', 'subcellular compartment', 'tissue', 'cell type',
      'organelle', 'virus', 'organelles', 'cell structure', 'plant', 'organism part'
    ],
    'chemical': [
      'metabolite', 'molecule', 'compound', 'chemical', 'hormone', 'phytohormone',
      'polysaccharide', 'material', 'polymer', 'chemical structure', 'biopolymer',
      'chemical compound', 'plant hormone', 'chemical group'
    ],
    'gene identifier': ['gene identifier'],
    'gene/protein': [
      'gene', 'protein', 'mutant', 'protein complex', 'enzyme', 'protein domain',
      'genetic element', 'gene family', 'protein family', 'protein structure', 'peptide',
      'protein motif', 'enzyme activity', 'protein region', 'gene feature', 'gene region',
      'gene structure', 'protein feature', 'transcription factor', 'gene cluster', 'gene group',
      'promoter', 'subunit', 'transcript', 'gene element', 'allele', 'protein sequence',
      'protein modification', 'post-translational modification', 'genetic locus',
      'protein subunit', 'genes', 'qtl', 'protein function', 'amino acid residue',
      'histone modification', 'protein fragment', 'receptor', 'genetic event', 'protein kinase',
      'protein class', 'protein group', 'gene product', 'antibody', 'proteins',
      'protein interaction', 'gene module'
    ],
    'genomic/transcriptomic feature': [
      'genomic region', 'genome', 'amino acid', 'genomic feature', 'dna sequence', 'rna',
      'sequence', 'mutation', 'chromosome', 'gene expression', 'genetic material', 'genotype',
      'genomic element', 'genetic marker', 'epigenetic mark', 'genetic variation',
      'regulatory element', 'epigenetic modification', 'dna element', 'mirna', 'genomic location',
      'subfamily', 'dna', 'activity', 'genetic feature', 'sequence motif', 'genetic variant',
      'motif', 'mrna', 'residue', 'region', 'genomic sequence', 'cis-element', 'clade',
      'accession', 'plasmid', 'genomic data', 'cultivar', 'genomic event', 'genomic resource',
      'ecotype', 'marker', 'lncrna', 'genetic construct', 'sequence feature', 'genus',
      'genetic concept'
    ],
    'method': [
      'method', 'technique', 'tool', 'database', 'software', 'dataset', 'concept', 'study',
      'description', 'model', 'modification', 'location', 'author', 'measurement', 'experiment',
      'researcher', 'mechanism', 'system', 'feature', 'parameter', 'algorithm', 'event',
      'reaction', 'resource', 'interaction', 'device', 'metric', 'technology', 'network',
      'construct', 'vector', 'category', 'data', 'research', 'geographical location',
      'document', 'analysis', 'person', 'project', 'research field', 'researchers',
      'gene network', 'relationship'
    ],
    'phenotype': ['phenotype'],
    'treatment': [
      'treatment', 'environment', 'condition', 'time', 'environmental factor', 'disease',
      'developmental stage', 'time point', 'stress', 'geographic location', 'abiotic stress',
      'time period'
    ]
  };
  console.log(filteredNodes);
  console.log(filteredEdges);
  /**
   * Initialize Cytoscape
   */
  let cy = cytoscape({
    container: document.getElementById('cy'), // HTML container
    autoungrabify: true, // Disable ungrabify on tap
    zoomingEnabled: true, // Enable zooming
    wheelSensitivity: 0.2, // Set custom wheel sensitivity
    textureOnViewport: false, // Allows rendering optimizations for large graphs
    elements: [...filteredNodes, ...filteredEdges], // Render nodes and edges
    motionBlur: false, // Enable motion blur for smoother animations
    motionBlurOpacity: 0.2, // Set opacity during motion blur
    pixelRatio: '1', // Set pixel ratio
    style: generateStyles(), // Apply styles to the graph
    layout: {
      name: 'preset', // Use the preset layout for initial positioning
    },
  });

  cy.ready(() => {
    cy.zoom(0.08);
    cy.pan({ x: 200, y: 0 });
  });

  /**
   * Generates node and edge styles for Cytoscape
   */
  function generateStyles() {
    const nodeStyles = {
      shapes: {
        'GENE IDENTIFIER': 'ellipse',
        'GENE/PROTEIN': 'ellipse',
        'PHENOTYPE': 'rectangle',
        'CELL/ORGAN/ORGANISM': 'hexagon',
        'CHEMICAL': 'diamond',
        'TREATMENT': 'pentagon',
        'NAN': 'star',
        'METHOD': 'triangle',
        'GENOMIC/TRANSCRIPTOMIC FEATURE': 'round-rectangle',
        'BIOLOGICAL PROCESS': 'diamond',
      },
      colors: {
        'GENE IDENTIFIER': '#FFD700',
        'GENE/PROTEIN': '#89CFF0',
        'PHENOTYPE': '#90EE90',
        'CELL/ORGAN/ORGANISM': '#FFB6C1',
        'CHEMICAL': '#98FB98',
        'TREATMENT': '#E0FFFF',
        'NAN': '#FFA07A',
        'METHOD': '#D2B48C',
        'GENOMIC/TRANSCRIPTOMIC FEATURE': '#AFEEEE',
        'BIOLOGICAL PROCESS': '#D8BFD8',
      },
      defaultShape: 'star',
      defaultColor: '#FFA07A',
    };

    const edgeStyles = {
      colors: {
        'ACTIVATION/INDUCTION/PROMOTION/CAUSATION/RESULT': '#32CD32',
        'REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION': '#DC143C',
        'REGULATION/CONTROL': '#4682B4',
        'EXPRESSION/DETECTION/IDENTIFICATION': '#FF8C00',
        'ASSOCIATION/CORRELATION/RELATION/INTERACTION/BINDING': '#8A2BE2',
        'LOCALIZATION/CONTAINMENT/COMPOSITION': '#3CB371',
        'REQUIREMENT/ESSENTIALITY/ACTIVITY/FUNCTION/PARTICIPATION': '#B22222',
        'ENCODING': '#4682B4',
        'SYNTHESIS/FORMATION': '#FF8C00',
        'OTHERS': '#C0C0C0',
      },
      arrows: {
        'ACTIVATION/INDUCTION/PROMOTION/CAUSATION/RESULT': 'triangle',
        'REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION': 'tee',
        'REGULATION/CONTROL': 'tee',
        'EXPRESSION/DETECTION/IDENTIFICATION': 'circle',
        'ASSOCIATION/CORRELATION/RELATION/INTERACTION/BINDING': 'circle',
        'LOCALIZATION/CONTAINMENT/COMPOSITION': 'circle',
        'REQUIREMENT/ESSENTIALITY/ACTIVITY/FUNCTION/PARTICIPATION': 'diamond',
        'ENCODING': 'circle',
        'SYNTHESIS/FORMATION': 'triangle',
        'OTHERS': 'triangle',
      },
      defaultColor: '#C0C0C0',
      defaultArrow: 'triangle',
    };

    return [
      // Node style
      {
        selector: 'node',
        style: {
          label: (ele) => ele.data('originalId'),
          width: '50px',
          height: '50px',
          color: '#000000',
          'font-size': '14px',
          'min-zoomed-font-size': 9,
          'text-halign': 'center',
          'text-valign': 'center',
          'text-wrap': 'wrap',
          'text-max-width': 30,
          shape: (ele) => nodeStyles.shapes[ele.data('category')] || nodeStyles.defaultShape,
          'background-color': (ele) => nodeStyles.colors[ele.data('category')] || nodeStyles.defaultColor,
        },
      },
      // Edge style
      {
        selector: 'edge',
        style: {
          width: 2,
          'line-color': (ele) => edgeStyles.colors[ele.data('category')] || edgeStyles.defaultColor,
          'target-arrow-color': (ele) => edgeStyles.colors[ele.data('category')] || edgeStyles.defaultColor,
          'target-arrow-shape': (ele) => edgeStyles.arrows[ele.data('category')] || edgeStyles.defaultArrow,
          'curve-style': 'bezier',
          'min-zoomed-font-size': 9,
          opacity: 0.8,
          label: (ele) => ele.data('interaction'),
          'font-size': '12px',
          'text-wrap': 'wrap',
          'text-max-width': 50,
          'text-rotation': 'autorotate',
          'text-margin-x': '9px',
          'text-margin-y': '-9px',
        },
      },
    ];
  }
  function isCentralNode(node) {
    // Suppose central nodes are those matching any of the queryTerms
    // in uppercase. If you prefer a different logic, adjust accordingly.
    return queryTerm.some((term) => node.id() === term);
  }
  /**
   * Function to style the central nodes
   */
  function styleCentralNodes(queryTerm) {
    cy.startBatch();
    //console.log(queryTerm);
    cy.nodes().forEach((node) => {
      if (queryTerm.some((term) => node.id() === term)) {
        node.style({
          width: '80px',
          height: '80px',
          opacity: 1,
          color: '#8B0000',
          'font-size': '25px',
          'text-halign': 'center',
          'text-valign': 'center',
          'text-wrap': 'wrap',
          'text-max-width': 50,
          'z-index': 9999,
        });
      }
    });
    cy.endBatch();
  }

  /**
   * Event Listeners
   */
  function initializeEventListeners() {
    // Node click listener
    cy.on('click', 'node', handleNodeClick);

    // Edge click listener
    cy.on('click', 'edge', handleEdgeClick);

    // Background click listener to reset or detect double-click
    let lastClickTime = 0;
    const doubleClickDelay = 300; // ms

    cy.on('click', (evt) => {
      if (evt.target === cy) {
        const currentTime = new Date().getTime();
        const timeDiff = currentTime - lastClickTime;
        if (timeDiff < doubleClickDelay) {
          // Double-click detected
          handleGraphDoubleClick();
        } else {
          // Single click => reset the view after doubleClickDelay
          setTimeout(() => {
            resetNetworkView();
          }, doubleClickDelay);
        }
        lastClickTime = currentTime;
      }
    });
  }

  /**
   * Node/Edge click handlers and related logic
   */
  let currentNode = null; // Stores the currently clicked node
  let removedEles = cy.collection(); // Stores removed elements for restoration

  function handleNodeClick(evt) {
    currentNode = evt.target;
    const neighborhood = currentNode.neighborhood().add(currentNode);

    highlightNeighborhood(neighborhood);
    showTooltipForNode(currentNode);

    updateNumNodes();
    updatePaperCount();
    updateNodeSummaries();
  }

  function handleEdgeClick(evt) {
    const edge = evt.target;
    highlightEdgeNeighborhood(edge);
    showTooltipForEdge(edge);

    updateNumNodes();
    updatePaperCount();
    updateNodeSummaries();
  }

  /**
   * Resets the network view to full opacity
   */
  function resetNetworkView() {
    cy.startBatch();
    cy.nodes().style('opacity', '1');
    cy.edges().style('opacity', '1');
    hideTooltip();
    toggleMinimizeHide();
    updateNodeSummaries();
    updateNumNodes();
    updatePaperCount();
    cy.endBatch();
  }

  /**
   * Removes the currently selected node from the network
   */
  function removeNode() {
    removedEles = removedEles.union(currentNode.remove());
    removedEles.push(currentNode.remove());
    updateNumNodes();
    updatePaperCount();
    updateNodeSummaries();
  }

  /**
   * Double-click on background to restore all nodes
   */
  function handleGraphDoubleClick() {
    console.log('Restoring removed nodes and resetting view');
    if (removedEles && removedEles.length > 0) {
      removedEles.restore();
    } else {
      console.log('No elements to restore');
    }
    cy.nodes().style('opacity', '1');
    hideTooltip();
    cy.fit();
    currentNode = null;
    updateNodeSummaries();
    updateNumNodes();
    updatePaperCount();
  }

  /**
   * Highlights a node's neighborhood
   */
  function highlightNeighborhood(neighborhood) {
    const nonNeighbors = cy.nodes().difference(neighborhood);

    cy.startBatch();
    neighborhood.style('opacity', '1');
    nonNeighbors.style('opacity', '0.5');
    cy.edges()
      .filter((edge) => nonNeighbors.contains(edge.source()) || nonNeighbors.contains(edge.target()))
      .style('opacity', '0.5');
    cy.endBatch();
  }

  /**
   * Highlights an edge's source and target nodes
   */
  function highlightEdgeNeighborhood(edge) {
    cy.startBatch();
    cy.nodes().style('opacity', '0.5');
    cy.edges().style('opacity', '0.5');

    edge.source().style('opacity', '1');
    edge.target().style('opacity', '1');
    edge.style('opacity', '1');

    cy.endBatch();
  }

  /**
   * Hides the tooltip
   */
  function hideTooltip() {
    document.getElementById('side-tooltip').style.display = 'none';
  }


  // Insert CSS into the document via JavaScript
  function insertTooltipCSS() {
    const css = `
      .tooltip-header {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 10px;
        color: #222;
      }
      .entity-value {
        color: #DC143C;
      }
      .edge-section {
        margin-top: 8px;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 15px;
        line-height: 1.5;
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 4px;
      }
      .edge-section p {
        margin: 5px 0;
        color: #666;
      }
      .btn-validate {
        margin-top: 10px;
        padding: 5px 10px;
        background-color: rgba(0, 0, 0, 0.6);
        color: white;
        border: none;
        cursor: pointer;
        border-radius: 4px;
      }
      /* Label colors for source, interaction and target */
      .label-source {
        color: #191970;
        font-weight: normal;
      }
      .label-interaction {
        color: #DC143C;
        font-weight: normal;
      }
      .label-target {
        color: #800000;
        font-weight: normal;
      }
    `;
    const style = document.createElement('style');
    style.type = "text/css";
    style.innerHTML = css;
    document.head.appendChild(style);
  }

  // Run the CSS insertion when the script loads
  insertTooltipCSS();

  /**
   * Displays a tooltip for a clicked node.
   * - If the disambiguated entity == original entity, show only "Entity."
   * - Otherwise, show "Disambiguated Entity" and "Original Entity."
   * - If the edge's disambiguated values equal the original values, display one line for the edge,
   *   appending the PMID in parentheses.
   *   Otherwise, display both "Connected Edge After Disambiguation:" and "Connected Edge Before Disambiguation:".
   *   All information is displayed expanded (not collapsed).
   */
  
  function showTooltipForNode(node) {
    const ab = document.getElementById('ab');
    const tooltip = document.getElementById('side-tooltip');
    const abTitle = document.getElementById('ab-title');
    const nodeinfo = document.getElementsByClassName('nodeinfo');
    const pmidElem = document.getElementById('pmid');
    const nodeId = node.data().originalId;
  
    // 🧼 Remove edge-only label: "Source Text:"
    const existingSourceText = document.querySelector('#side-tooltip label.source-text');
    if (existingSourceText) {
      existingSourceText.remove();
    }
    pmidElem.innerHTML = '';
    pmidElem.style.display = 'none';
  
    // Reveal nodeinfo elements
    Array.from(nodeinfo).forEach(elem => (elem.style.display = 'block'));
  
    // ✅ Inject "Actions:" label before <ul> (remove duplicates first)
    Array.from(nodeinfo).forEach(div => {
      const existingActionsLabel = div.querySelector('.node-actions-label');
      if (existingActionsLabel) {
        existingActionsLabel.remove();
      }
  
      const actionsLabel = document.createElement("label");
      actionsLabel.className = "title node-actions-label";
      actionsLabel.textContent = "Actions:";
      const ul = div.querySelector("ul");
      if (ul) {
        div.insertBefore(actionsLabel, ul);
      }
    });
    // Reveal nodeinfo elements
    Array.from(nodeinfo).forEach(elem => (elem.style.display = 'block'));
  
    // Check if node is the same as original.
    // (This example compares the disambiguated id with originalId_beforedisamb.
    // If they differ, we assume disambiguation has occurred.)
    const isSameEntity =
      node.data().originalId === node.data().originalId_beforedisamb &&
      node.data().type === node.data().type_beforedisamb;
  
    // Create a formatted display string for the original entity(ies)
    let originalEntityDisplay = "";
    const origIds = node.data().originalId_beforedisamb;
    const origTypes = node.data().type_beforedisamb;
  
    if (Array.isArray(origIds)) {
      // If the original IDs are stored in an array,
      // display each on a new line.
      // If original types is an array too, match by index.
      if (Array.isArray(origTypes)) {
        originalEntityDisplay = origIds
          .map((id, idx) => `${id} [${origTypes[idx]}]`)
          .join("<br>");
      } else {
        originalEntityDisplay = origIds.join("<br>");
      }
    } else {
      // Otherwise, just format the single original id.
      originalEntityDisplay = `${origIds} [${origTypes}]`;
    }
  
    // Build the header HTML for the tooltip
    let nodeHeaderHTML = '';
    if (isSameEntity) {
      nodeHeaderHTML = `
        <div class="tooltip-header">
          Entity: <span class="entity-value">${nodeId} [${node.data().type}]</span>
        </div>
      `;
    } else {
      nodeHeaderHTML = `
        <div class="tooltip-header">
          Resolved Entity: <span class="entity-value">${nodeId} [${node.data().type}]</span><br><br>
          Original Entity:<br>
          <span class="entity-value">${originalEntityDisplay}</span>
        </div>
      `;
    }
    pmidElem.innerHTML = '';
    abTitle.innerHTML = nodeHeaderHTML;
  
    // Build content for connected edges
    let edgeInfoHTML = '';
  
    node.connectedEdges().forEach(edge => {
      // Determine if the clicked node is the source or target
      const isSource = edge.data().source === node.data().id;
      // Use color #191970 if node is source, else #800000
      const definitionColor = isSource ? "#191970" : "#800000";
  
      // The “2” definitions and labels
      const extractedDefinition2 = isSource
        ? edge.data().source_extracted_definition
        : edge.data().target_extracted_definition;
      const generatedDefinition2 = isSource
        ? edge.data().source_generated_definition
        : edge.data().target_generated_definition;
      const labelEntity2 = isSource
        ? `${edge.data().originalsource2} [${edge.data().sourcetype2}]`
        : `${edge.data().originaltarget2} [${edge.data().targettype2}]`;
  
      // Disambiguated edge fields
      const originalSource = edge.data().originalsource;
      const sourceType = edge.data().sourcetype;
      const interaction = edge.data().interaction;
      const originalTarget = edge.data().originaltarget;
      const targetType = edge.data().targettype;
  
      // Original edge fields
      const originalsource2 = edge.data().originalsource2 || 'N/A';
      const sourcetype2 = edge.data().sourcetype2 || 'N/A';
      const interaction2 = edge.data().interaction2 || 'N/A';
      const originaltarget2 = edge.data().originaltarget2 || 'N/A';
      const targettype2 = edge.data().targettype2 || 'N/A';
  
      // Check if the entire edge is identical (before and after disambiguation)
      const isEdgeSame =
        originalSource === originalsource2 &&
        sourceType === sourcetype2 &&
        interaction === interaction2 &&
        originalTarget === originaltarget2 &&
        targetType === targettype2;
  
      // Build the connected edge display
      let edgeLinesHTML = '';
      if (isEdgeSame) {
        edgeLinesHTML = `
          <p>
            <strong>Connected Edge:</strong>
            <span class="label-source">${originalSource} [${sourceType}]</span>
            <span class="label-interaction">${interaction}</span>
            <span class="label-target">${originalTarget} [${targetType}]</span>
            <span style="cursor:pointer; color: blue; text-decoration: underline;" onclick="openPMIDModal(
              '${edge.data().pmid}',
              '${edge.data().originalsource} [${edge.data().sourcetype}]',
              '${edge.data().interaction}',
              '${edge.data().originaltarget} [${edge.data().targettype}]'
            )"> (${edge.data().pmid})</span>
          </p>
        `;
      } else {
        edgeLinesHTML = `
          <p>
            <strong>Resolved Connected Edge:</strong>
            <span class="label-source">${originalSource} [${sourceType}]</span>
            <span class="label-interaction">${interaction}</span>
            <span class="label-target">${originalTarget} [${targetType}]</span>
            <span style="cursor:pointer; color: blue; text-decoration: underline;" onclick="openPMIDModal(
              '${edge.data().pmid}',
              '${edge.data().originalsource} [${edge.data().sourcetype}]',
              '${edge.data().interaction}',
              '${edge.data().originaltarget} [${edge.data().targettype}]'
            )"> (${edge.data().pmid})</span>
          </p>
          <p>
            <strong>Original Connected Edge:</strong>
            <span class="label-source">${originalsource2} [${sourcetype2}]</span>
            <span class="label-interaction">${interaction2}</span>
            <span class="label-target">${originaltarget2} [${targettype2}]</span>
          </p>
        `;
      }
  
      // Build the definitions section with dynamic labels
      edgeInfoHTML += `
        <div class="edge-section">
          ${edgeLinesHTML}
          <p>
            <strong style="color:${definitionColor};">
              ${isSource ? 'Source Definitions:' : 'Target Definitions:'}
            </strong>
          </p>
          <p>
            <strong style="color:${definitionColor};">
              ${isSource ? 'Source' : 'Target'} Extracted Definition for ${labelEntity2}:
            </strong>
            ${extractedDefinition2 || 'N/A'}
          </p>
          <p>
            <strong style="color:${definitionColor};">
              ${isSource ? 'Source' : 'Target'} Generated Definition for ${labelEntity2}:
            </strong>
            ${generatedDefinition2 || 'N/A'}
          </p>
        </div>
      `;
    });
  
    ab.innerHTML = edgeInfoHTML;
    tooltip.style.display = 'block';
  }

  /**
  * Displays a tooltip for a clicked edge.
  * - If the disambiguated interaction == original interaction, show only "Interaction."
  * - Otherwise, show "Disambiguated Interaction" and "Original Interaction."
  * - If entire edge is identical after disambiguation, only show 1 line in connected edge details.
  */
  function showTooltipForEdge(edge) {
    const tooltip = document.getElementById('side-tooltip');
    const ab = document.getElementById('ab');
    const abTitle = document.getElementById('ab-title');
    const pmidElem = document.getElementById('pmid');
    const nodeinfo = document.getElementsByClassName('nodeinfo');
    const edgeinfo2 = document.getElementsByClassName('edgeinfo2');
  
    // Hide nodeinfo elements and reveal edgeinfo2 elements
    Array.from(nodeinfo).forEach(elem => (elem.style.display = 'none'));
    Array.from(edgeinfo2).forEach(elem => (elem.style.display = 'block'));
  
    // Check if interaction is the same
    const isSameInteraction = edge.data().interaction === edge.data().interaction2;
    let edgeHeaderHTML = '';
    if (isSameInteraction) {
      edgeHeaderHTML = `
        <div class="tooltip-header">
          Relationship: <span class="entity-value">${edge.data().interaction}</span>
        </div>
      `;
    } else {
      edgeHeaderHTML = `
        <div class="tooltip-header">
          Resolved Relationship: <span class="entity-value">${edge.data().interaction}</span><br><br>
          Original Relationship: <span class="entity-value">${edge.data().interaction2}</span>
        </div>
      `;
    }
    abTitle.innerHTML = edgeHeaderHTML;
  
    // Disambiguated fields
    const originalSource = edge.data().originalsource;
    const sourceType = edge.data().sourcetype;
    const interaction = edge.data().interaction;
    const originalTarget = edge.data().originaltarget;
    const targetType = edge.data().targettype;
  
    // Original fields
    const originalsource2 = edge.data().originalsource2;
    const sourcetype2 = edge.data().sourcetype2;
    const interaction2 = edge.data().interaction2;
    const originaltarget2 = edge.data().originaltarget2;
    const targettype2 = edge.data().targettype2;
  
    // Check if entire edge is the same
    const isEdgeSame =
      originalSource === originalsource2 &&
      sourceType === sourcetype2 &&
      interaction === interaction2 &&
      originalTarget === originaltarget2 &&
      targetType === targettype2;
  
    // Build connected edge detail line(s)
    let connectedEdgeLineHTML = '';
    if (isEdgeSame) {
      connectedEdgeLineHTML = `
        <p>
          <strong>Connected Edge:</strong>
          <span class="label-source">${originalSource} [${sourceType}]</span>
          <span class="label-interaction">${interaction}</span>
          <span class="label-target">${originalTarget} [${targetType}]</span>
        </p>
      `;
    } else {
      connectedEdgeLineHTML = `
        <p>
          <strong>Resolved Connected Edge:</strong>
          <span class="label-source">${originalSource} [${sourceType}]</span>
          <span class="label-interaction">${interaction}</span>
          <span class="label-target">${originalTarget} [${targetType}]</span>
        </p>
        <p>
          <strong>Original Connected Edge:</strong>
          <span class="label-source">${originalsource2} [${sourcetype2}]</span>
          <span class="label-interaction">${interaction2}</span>
          <span class="label-target">${originaltarget2} [${targettype2}]</span>
        </p>
      `;
    }
  
    // Build the edge details content (all content expanded)
    ab.innerHTML = `
      <div class="edge-section">
        <div class="edge-details">
          <div class="edge-info">
            ${connectedEdgeLineHTML}
            <p><strong>Species:</strong> ${edge.data().species}</p>
            <p><strong>Edge Basis:</strong> ${edge.data().basis}</p>
          </div>
          <div class="definition-section">
            <p><strong style="color:#191970;">Source Definitions:</strong></p>
            <p>
              <strong style="color:#191970;">${originalSource} [${sourceType}] Extracted Definition:</strong>
              ${edge.data().source_extracted_definition || 'No definition available'}
            </p>
            <p>
              <strong style="color:#191970;">${originalSource} [${sourceType}] Generated Definition:</strong>
              ${edge.data().source_generated_definition || 'No definition available'}
            </p>
          </div>
          <div class="definition-section">
            <p><strong style="color:#800000;">Target Definitions:</strong></p>
            <p>
              <strong style="color:#800000;">${originalTarget} Extracted Definition:</strong>
              ${edge.data().target_extracted_definition || 'No definition available'}
            </p>
            <p>
              <strong style="color:#800000;">${originalTarget} Generated Definition:</strong>
              ${edge.data().target_generated_definition || 'No definition available'}
            </p>
          </div>
        </div>
      </div>
      
      <button id="validateEdge" class="btn-validate">Validate Edge</button>
    `;
  
    // Set the PMID link and action
    const pmidValue = edge.data().pmid;
    // Remove any existing 'Source Text' label if present
    const existingSourceLabel = document.querySelector('#side-tooltip label.title.source-text');
    if (existingSourceLabel) {
      existingSourceLabel.remove();
    }

    // Show "Source Text" label only for edges
    const sourceTextLabel = document.createElement("label");
    sourceTextLabel.className = "title source-text";
    sourceTextLabel.textContent = "Source Text:";
    pmidElem.parentNode.insertBefore(sourceTextLabel, pmidElem);
    pmidElem.innerHTML = `PMID: ${pmidValue}`;
    pmidElem.style.display = 'block';
    pmidElem.onclick = () =>
      openPMIDModal(
        pmidValue,
        `${edge.data().originalsource} [${edge.data().sourcetype}]`,
        edge.data().interaction,
        `${edge.data().originaltarget} [${edge.data().targettype}]`
      );
  
    // Add event listener to the validate button
    document.getElementById('validateEdge').addEventListener('click', () => {
      validateEdgeAPI(
        edge.data().pmid,
        `${edge.data().originalsource2} [${edge.data().sourcetype2}]`,
        edge.data().interaction,
        `${edge.data().originaltarget2} [${edge.data().targettype2}]`
      );
    });
  
    tooltip.style.display = 'block';
  }


  /**
   * Function to handle API validation and display streamed results
   */
  function validateEdgeAPI(p_source, source, interaction, target) {
    console.log("📡 Sending request to /process-text:", { p_source, source, interaction, target });

    let resultContainer = document.getElementById('validationResult');
    const cyWrapper = document.getElementById('cy_wrapper');

    // If validationResult is not inside cy_wrapper, move it there
    if (!cyWrapper.contains(resultContainer)) {
      resultContainer.remove(); // Remove old instance
      resultContainer = document.createElement('div');
      resultContainer.id = 'validationResult';
      cyWrapper.appendChild(resultContainer);
    }

    // Style the container
    resultContainer.style.position = 'absolute';
    resultContainer.style.bottom = '0px';
    resultContainer.style.left = '0px';
    resultContainer.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
    resultContainer.style.color = '#333';
    resultContainer.style.padding = '10px'; // Reduced padding
    resultContainer.style.borderRadius = '8px';
    resultContainer.style.boxShadow = '0px 4px 8px rgba(0, 0, 0, 0.2)';
    resultContainer.style.width = '320px';
    resultContainer.style.height = '100%';
    resultContainer.style.zIndex = '9999';
    resultContainer.style.display = 'block';
    resultContainer.innerHTML = ""; // Clear previous results

    // Create a header with a minimize button
    const header = document.createElement("div");
    header.style.background = '#007BFF';
    header.style.color = 'white';
    header.style.padding = '5px'; // Reduced header padding
    header.style.fontWeight = 'bold';
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'center';
    header.style.borderTopLeftRadius = '8px';
    header.style.borderTopRightRadius = '8px';
    header.innerHTML = "<span>API Validation Results</span><span style='cursor:pointer;' onclick='toggleMinimize()'>➖</span>";
    resultContainer.appendChild(header);

    // Create a content container
    const resultBox = document.createElement('div');
    resultBox.classList.add('summary-container');
    resultBox.style.border = '1px solid #ddd';
    resultBox.style.padding = '8px'; 
    resultBox.style.margin = '0';
    resultBox.style.backgroundColor = '#f8f9fa';
    resultBox.style.fontFamily = 'Arial, sans-serif';
    resultBox.style.fontSize = '14px';
    resultBox.style.lineHeight = '1.5';
    resultBox.style.height = '95%';
    resultBox.style.maxHeight = '95%';
    resultBox.style.overflowY = 'auto';
    resultContainer.appendChild(resultBox);

    // Create a single paragraph inside the container
    const paragraph = document.createElement("p");
    paragraph.style.margin = '0';
    paragraph.style.color = '#333';
    resultBox.appendChild(paragraph);

    let accumulatedText = ""; // Store incoming text chunks

    fetch('/process-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_source, source, interaction, target })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Server Error: ${response.statusText}`);
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      function readStream() {
        return reader.read().then(({ done, value }) => {
          if (done) {
            console.log("✅ Stream completed");
            return;
          }
          // Decode and accumulate the chunk
          const chunk = decoder.decode(value, { stream: true });
          accumulatedText += chunk;

          // Render the text as Markdown
          paragraph.innerHTML = marked.parse(accumulatedText);

          // Continue reading until done
          return readStream();
        });
      }
      return readStream();
    })
    .catch(error => {
      console.error("❌ Error validating edge:", error);
      paragraph.style.color = '#D32F2F';
      paragraph.innerHTML = `<strong>Error:</strong> ${error.message}`;
    });
  }

  // Minimize/hide functions for the validation result container
  function toggleMinimize() {
    const resultContainer = document.getElementById('validationResult');
    const resultBox = document.querySelector('#validationResult .summary-container');
    
    const minimizedHeight = '55px';
    if (resultBox) {
      if (resultBox.style.display === 'none') {
        // If hidden, show
        resultBox.style.display = 'block';
        resultContainer.style.height = '100%';
      } else {
        // If visible, hide
        resultBox.style.display = 'none';
        resultContainer.style.height = minimizedHeight;
      }
    }
  }
  function toggleHide() {
    const resultContainer = document.getElementById('validationResult');
    if (resultContainer) {
      resultContainer.style.display = 'none';
    }
  }
  function toggleMinimizeHide() {
    const resultContainer = document.getElementById('validationResult');
    if (!resultContainer) return;
    const resultBox = resultContainer.querySelector('.summary-container');
    if (resultBox) {
      resultBox.style.display = 'none';
      resultContainer.style.height = '55px';
    }
  }

  /**
   * Opens a modal to show more details for a given PMID
   */
  function openPMIDModal(pmid, originalSource, interaction, originalTarget) {
    addModalContent(pmid, originalSource, interaction, originalTarget);
    console.log(`Opening modal for PMID: ${pmid}`);
  }

  /**
   * Node filter form handling
   */
  function openNodeFilterForm() {
    edgecloseForm();
    const nodeFilterForm = document.getElementById('nodeFilterForm');
    nodeFilterForm.style.display =
      nodeFilterForm.style.display === 'none' || nodeFilterForm.style.display === ''
        ? 'block'
        : 'none';
  }
  function nodecloseForm() {
    document.getElementById('nodeFilterForm').style.display = 'none';
  }

  /**
   * Edge filter form handling
   */
  function openEdgeFilterForm() {
    nodecloseForm();
    const edgeFilterForm = document.getElementById('edgeFilterForm');
    edgeFilterForm.style.display =
      edgeFilterForm.style.display === 'none' || edgeFilterForm.style.display === ''
        ? 'block'
        : 'none';
  }
  function edgecloseForm() {
    document.getElementById('edgeFilterForm').style.display = 'none';
  }

  /**
   * Utility function to determine node category from its type
   */
  function getNodeCategory(nodeType) {
    for (const category in categoryMap) {
      if (categoryMap[category].includes(nodeType)) {
        return category;
      }
    }
    return 'Others';
  }

  /**
   * Updates the number of visible nodes in the network
   */
  function updateNumNodes() {
    const visibleNodes = cy.nodes().filter(
      (node) => node.visible() && parseFloat(node.style('opacity')) === 1
    ).length;
    document.getElementById('element-len').textContent = `${visibleNodes} nodes`;
  }

  /**
   * Updates the number of papers (PMIDs) related to the visible edges
   */
  function updatePaperCount() {
    const pmids = new Set();
    cy.edges()
      .filter((edge) => edge.visible() && parseFloat(edge.style('opacity')) === 1)
      .forEach((edge) => {
        const pmid = edge.data('p_source');
        if (pmid) pmids.add(pmid);
      });
    document.getElementById('number-papers').textContent = `${pmids.size}`;
  }

  /**
   * Isolates the selected node’s neighborhood
   */
  function isolateNeighborhood() {
    cy.startBatch();
    const neighborhood = currentNode.neighborhood().add(currentNode);
    removedEles = cy.elements().difference(neighborhood).remove();

    updateNumNodes();
    updatePaperCount();
    updateNodeSummaries();

    const layout = neighborhood.layout({
      name: 'cose',
      animate: false,
      padding: 10,
      fit: true,
      nodeDimensionsIncludeLabels: true,
    });
    layout.run();

    cy.endBatch();
  }

  /**
   * Summaries
   */
  function updateNodeSummaries() {
    const networkSummaryDiv = document.getElementById('networkSummary');
    if (!networkSummaryDiv) {
      console.error("Element with id 'networkSummary' not found!");
      return;
    }

    const nodeSummaries = {};
    const visibleEdges = cy
      .edges()
      .filter((edge) => edge.visible() && parseFloat(edge.style('opacity')) === 1)
      .map((edge) => ({
        source: edge.data().originalsource + ' [' + edge.data().sourcetype + ']',
        interaction: edge.data().interaction,
        target: edge.data().originaltarget + ' [' + edge.data().targettype + ']',
        pmid: edge.data().pmid,
      }));

    visibleEdges.forEach((edge) => {
      const { source, interaction, target, pmid } = edge;
      if (!nodeSummaries[source]) {
        nodeSummaries[source] = {};
      }
      const key = interaction;
      if (!nodeSummaries[source][key]) {
        nodeSummaries[source][key] = [];
      }
      nodeSummaries[source][key].push({ target, pmid });
    });

    // Sort by number of unique interactions
    const sortedNodes = Object.keys(nodeSummaries)
      .map((source) => {
        const totalInteractions = Object.keys(nodeSummaries[source]).length;
        return {
          source,
          totalInteractions,
          summaries: nodeSummaries[source],
        };
      })
      .sort((a, b) => b.totalInteractions - a.totalInteractions);

    let summaryText = '';
    sortedNodes.forEach((node) => {
      summaryText += `<span style='color: #191970;'>${node.source} </span>`;
      const summaries = node.summaries;
      let firstInteraction = true;

      for (const [interaction, value] of Object.entries(summaries)) {
        const targets = value
          .map(
            ({ target, pmid }) => `
              <span style='color: #800000;'>${target}</span> 
              (PMID: <a class="tooltippubmed-link tooltippubmed-hyperlink" href="javascript:void(0)"
                data-pmid="${pmid}" data-source="${node.source}" data-interaction="${interaction}"
                data-target="${target}">${pmid}</a>)
            `
          )
          .join(', ');

        if (!firstInteraction) {
          summaryText += '; ';
        }
        summaryText += `<span style='color: #DC143C;'>${interaction}</span> ${targets}`;
        firstInteraction = false;
      }
      summaryText += '.<br><br>';
    });

    networkSummaryDiv.innerHTML = summaryText;

    // PubMed link event
    document.querySelectorAll('.tooltippubmed-link').forEach((link) => {
      const pmidValue = link.getAttribute('data-pmid');
      const source = link.getAttribute('data-source');
      const interaction = link.getAttribute('data-interaction');
      const target = link.getAttribute('data-target');

      link.onclick = () => openPMIDModal(pmidValue, source, interaction, target);
    });
  }

  /**
   * Show definitions for the search term
   */
  function showDefinitionsForSearchTerm(queryTerms) {
    const nodeSummary = document.getElementById('nodeSummary');
    const itemsPerPage = 5;
    let extractedDefinitions = [];
    let generatedDefinitions = [];
    let found = false;
    const uniqueDefinitions = new Set();
    const edgesArray = cy.edges().toArray();

    for (let i = 0; i < edgesArray.length; i++) {
      const edge = edgesArray[i];
      const pmidValue = edge.data().pmid;
      const sourceUpper = edge.data().source;
      const targetUpper = edge.data().target;

      const isSourceMatch = queryTerms.some((term) => sourceUpper.includes(term.toUpperCase()));
      const isTargetMatch = queryTerms.some((term) => targetUpper.includes(term.toUpperCase()));

      if (isSourceMatch || isTargetMatch) {
        found = true;
        const createDefinitionKey = (definition, pmid) => `${definition}-${pmid}`;

        // Source extracted definition
        if (
          isSourceMatch &&
          edge.data().source_extracted_definition &&
          edge.data().source_extracted_definition !== 'nan'
        ) {
          const entitynametype = `${edge.data().originalsource} [${edge.data().sourcetype}]`;
          const definitionKey = createDefinitionKey(edge.data().source_extracted_definition, pmidValue);
          if (!uniqueDefinitions.has(definitionKey)) {
            uniqueDefinitions.add(definitionKey);
            extractedDefinitions.push(`
              <li style="margin-bottom: 8px; color: #000000;">
                ${entitynametype}: ${edge.data().source_extracted_definition}
                (PMID: <a class="tooltippubmed-link tooltippubmed-hyperlink" href="javascript:void(0)" 
                  data-pmid="${pmidValue}" data-source="${entitynametype}" data-interaction="${edge.data().interaction}"
                  data-target="${edge.data().originaltarget} [${edge.data().targettype}]">
                  ${pmidValue}
                </a>)
              </li>
            `);
          }
        }

        // Target extracted definition
        if (
          isTargetMatch &&
          edge.data().target_extracted_definition &&
          edge.data().target_extracted_definition !== 'nan'
        ) {
          const entitynametype = `${edge.data().originaltarget} [${edge.data().targettype}]`;
          const definitionKey = createDefinitionKey(edge.data().target_extracted_definition, pmidValue);
          if (!uniqueDefinitions.has(definitionKey)) {
            uniqueDefinitions.add(definitionKey);
            generatedDefinitions.push(`
              <li style="margin-bottom: 8px; color: #000000;">
                ${entitynametype}: ${edge.data().target_extracted_definition} 
                (PMID: <a class="tooltippubmed-link tooltippubmed-hyperlink" href="javascript:void(0)" 
                  data-pmid="${pmidValue}" data-source="${edge.data().originalsource} [${edge.data().sourcetype}]"
                  data-interaction="${edge.data().interaction}" data-target="${entitynametype}">
                  ${pmidValue}
                </a>)
              </li>
            `);
          }
        }

        // Source generated definition
        if (
          isSourceMatch &&
          edge.data().source_generated_definition &&
          edge.data().source_generated_definition !== 'nan'
        ) {
          const entitynametype = `${edge.data().originalsource} [${edge.data().sourcetype}]`;
          const definitionKey = createDefinitionKey(edge.data().source_generated_definition, pmidValue);
          if (!uniqueDefinitions.has(definitionKey)) {
            uniqueDefinitions.add(definitionKey);
            generatedDefinitions.push(`
              <li style="margin-bottom: 8px; color: #000000;">
                ${entitynametype}: ${edge.data().source_generated_definition} 
                (PMID: <a class="tooltippubmed-link tooltippubmed-hyperlink" href="javascript:void(0)" 
                  data-pmid="${pmidValue}" data-source="${entitynametype}" data-interaction="${edge.data().interaction}"
                  data-target="${edge.data().originaltarget} [${edge.data().targettype}]">
                  ${pmidValue}
                </a>)
              </li>
            `);
          }
        }

        // Target generated definition
        if (
          isTargetMatch &&
          edge.data().target_generated_definition &&
          edge.data().target_generated_definition !== 'nan'
        ) {
          const entitynametype = `${edge.data().originaltarget} [${edge.data().targettype}]`;
          const definitionKey = createDefinitionKey(edge.data().target_generated_definition, pmidValue);
          if (!uniqueDefinitions.has(definitionKey)) {
            uniqueDefinitions.add(definitionKey);
            generatedDefinitions.push(`
              <li style="margin-bottom: 8px; color: #000000;">
                ${entitynametype}: ${edge.data().target_generated_definition} 
                (PMID: <a class="tooltippubmed-link tooltippubmed-hyperlink" href="javascript:void(0)" 
                  data-pmid="${pmidValue}" data-source="${edge.data().originalsource} [${edge.data().sourcetype}]"
                  data-interaction="${edge.data().interaction}" data-target="${entitynametype}">
                  ${pmidValue}
                </a>)
              </li>
            `);
          }
        }
      }
    }

    renderDefinitions();

    function renderDefinitions() {
      extractedDefinitions = extractedDefinitions
      .filter((item) => item && !item.includes('nan') && !item.includes('None'))
      .slice(0, 50);
    
    generatedDefinitions = generatedDefinitions
      .filter((item) => item && !item.includes('nan') && !item.includes('None'))
      .slice(0, 50);

      if (found) {
        nodeSummary.innerHTML = `
          <p><span class="lead">Entity Definitions: </span></p>
          <div id="extractedDefinitionsContainer"></div>
          <div id="generatedDefinitionsContainer"></div>
          <div id="paginationControls" style="margin-top: 20px;"></div>
          <!-- <p><span class="lead">Node summary of the network: </span></p> -->
        `;
        showPage(1);
      } else {
        nodeSummary.innerHTML = `<p></p>`;
      }
    }

    function showPage(page) {
      const start = (page - 1) * itemsPerPage;
      const end = start + itemsPerPage;

      const extractedContent = extractedDefinitions.slice(start, end).join('') ||
        '<p>No extracted definitions on this page.</p>';
      document.getElementById('extractedDefinitionsContainer').innerHTML = `
        <div style="margin-bottom: 8px;">
          <strong style="color: #191970;">Extracted Definitions (Page ${page}):</strong>
          ${extractedContent}
        </div>
      `;

      const generatedContent = generatedDefinitions.slice(start, end).join('') ||
        '<p>No generated definitions on this page.</p>';
      document.getElementById('generatedDefinitionsContainer').innerHTML = `
        <div style="margin-bottom: 8px;">
          <strong style="color: #800000;">Generated Definitions (Page ${page}):</strong>
          ${generatedContent}
        </div>
      `;
      addPaginationControls(page);
    }

    function addPaginationControls(currentPage) {
      const paginationDiv = document.getElementById('paginationControls');
      paginationDiv.innerHTML = '';
      const totalPages = Math.ceil(
        Math.max(extractedDefinitions.length, generatedDefinitions.length) / itemsPerPage
      );

      const nav = document.createElement('nav');
      nav.setAttribute('aria-label', 'Pagination');
      const ul = document.createElement('ul');
      ul.classList.add('pagination', 'text-center');

      for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.classList.add('page-item');
        const pageLink = document.createElement('a');
        pageLink.classList.add('page-link');
        pageLink.textContent = i;
        pageLink.href = '#';
        pageLink.style.marginRight = '5px';
        pageLink.onclick = (e) => {
          e.preventDefault();
          showPage(i);
        };

        if (i === currentPage) {
          li.classList.add('active');
          pageLink.setAttribute('aria-current', 'page');
        }
        li.appendChild(pageLink);
        ul.appendChild(li);
      }

      nav.appendChild(ul);
      paginationDiv.appendChild(nav);
    }
  }

  /**
   * ----------------------------
   * 2) NEW CODE (Edge-Group + Combined Filter)
   * ----------------------------
   */

  /***********************************************************
   * STATIC CATEGORY MAPPING
   ***********************************************************/
  const CATEGORY_MAPPING = {
    "ACTIVATION/INDUCTION/PROMOTION/CAUSATION/RESULT": [
      "ACTIVATES","ACTIVATE","ACTIVATED","UPREGULATES","UP-REGULATED","UP-REGULATED BY","INDUCED",
      "INDUCES","STIMULATES","ENHANCES","PROMOTES","INCREASED","INCREASES","INDUCES EXPRESSION OF",
      "INDUCED EXPRESSION OF","ACTIVATED BY","IS ACTIVATED BY","INCREASE","UP-REGULATES",
      "UPREGULATED UNDER","TRIGGERED","CAUSES","CAUSED","CAUSED BY","RESULTS IN","RESULTED IN",
      "RESULTS","RESULT IN","LED TO","LEADS TO","TRIGGER","TRIGGERS","INDUCES","INDUCED","CONTRIBUTED TO"
    ],
    "REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION": [
      "REPRESSES","REPRESSED","REPRESSED BY","INHIBITS","INHIBITED","INHIBITED BY","SUPPRESSES",
      "SUPPRESSED","NEGATIVELY REGULATES","NEGATIVELY REGULATE","DOWNREGULATES","DOWN-REGULATED",
      "DOWN-REGULATED BY","REPRESS","DECREASES","DECREASED","DECREASE","REDUCED","REDUCE","REDUCTION",
      "REDUCED IN","LOWER","LOWERED","LOWER IN","HAD LOWER","HAD HIGHER","WAS HIGHER IN","LACKED","LACKING"
    ],
    "REGULATION/CONTROL": [
      "REGULATES","REGULATING","REGULATED BY","CONTROL","CONTROLS","IS REGULATED BY","IS CONTROLLED BY",
      "CONTROLLED BY","MODULATES","MODULATED","AFFECT","AFFECTS","AFFECTED","AFFECTED BY","INFLUENCE",
      "INFLUENCES","INFLUENCED","INFLUENCED BY","MEDIATES","MEDIATED","IS MEDIATED BY","MEDIATED BY",
      "REGULATES EXPRESSION OF","IS REGULATED BY","IS A COMPONENT OF","IS IMPORTANT FOR","PLAYS A ROLE IN",
      "PLAY ROLES IN","PLAYS IMPORTANT ROLES IN","PLAY AN IMPORTANT ROLE IN","PLAYS AN IMPORTANT ROLE IN"
    ],
    "EXPRESSION/DETECTION/IDENTIFICATION": [
      "EXPRESSES","EXPRESSED","EXPRESSING","IS EXPRESSED IN","IS HIGHLY EXPRESSED IN","WAS EXPRESSED IN",
      "DETECTED","DETECTED IN","DETECTED BY","IDENTIFIED","IDENTIFIED IN","IDENTIFIED BY","WAS IDENTIFIED IN",
      "OBSERVED","OBSERVED IN","DISPLAYED","DISPLAYS","REVEALED","REVEALS","REPORTED IN","INDICATES",
      "SUGGESTS","INVESTIGATED IN","CHARACTERIZED IN","STUDIED IN","WAS DETECTED IN"
    ],
    "ASSOCIATION/CORRELATION/RELATION/INTERACTION/BINDING": [
      "ASSOCIATED WITH","ASSOCIATES WITH","IS ASSOCIATED WITH","IS LINKED TO","LINKED TO","IS LINKED WITH",
      "LINKED WITH","CORRELATES WITH","CORRELATED WITH","POSITIVELY CORRELATED WITH","NEGATIVELY CORRELATED WITH",
      "RELATED TO","IS RELATED TO","BINDS","BIND","BOUND TO","BINDS TO","BIND TO","INTERACTS WITH",
      "INTERACT WITH","INTERACTION WITH","INTERACTED WITH","FORMS COMPLEX WITH"
    ],
    "LOCALIZATION/CONTAINMENT/COMPOSITION": [
      "LOCALIZED IN","LOCALIZED TO","IS LOCALIZED TO","IS LOCALIZED IN","LOCATED IN","LOCATED AT",
      "LOCATED ON","IS LOCATED IN","CONTAINS","CONTAINED","CONTAIN","INCLUDES","INCLUDED","INCLUDE",
      "INCLUDING","COMPRISES","COMPOSED OF","CONSISTS OF","IS COMPOSED OF","COMPRISE","CONSIST OF",
      "IS PART OF","PART OF","HARBORS","POSSESSES","POSSESS","HAS","HAVE","BELONGS TO"
    ],
    "REQUIREMENT/ESSENTIALITY/ACTIVITY/FUNCTION/PARTICIPATION": [
      "REQUIRED FOR","IS REQUIRED FOR","REQUIRES","REQUIRE","IS NECESSARY FOR","NECESSARY FOR",
      "ESSENTIAL FOR","ARE ESSENTIAL FOR","PLAYS ROLE IN","REQUIRED","ACTIVITY","ACTIVATES","ACTIVATE",
      "ACTIVATED","ACTS AS","ACTS IN","ACTS DOWNSTREAM OF","ACTS UPSTREAM OF","PARTICIPATES IN",
      "PARTICIPATE IN","INVOLVES","IS INVOLVED IN","INVOLVED IN","FUNCTIONS AS","FUNCTIONS IN",
      "FUNCTION AS","FUNCTION IN","USES","UTILIZES"
    ],
    "ENCODING": [
      "ENCODES","ENCODED","ENCODED BY","IS ENCODED BY","ENCODES FOR","ENCODING"
    ],
    "SYNTHESIS/FORMATION": [
      "SYNTHESIZES","SYNTHESIZED","SYNTHESIS","SYNTHESIZED BY","FORMS","FORMED","FORMS COMPLEX WITH","SYNTHESIZE",
      "FORMED COMPLEX WITH"
    ]
  };

  /***********************************************************
   * Map group => the above CATEGORY_MAPPING key
   ***********************************************************/
  const GROUP_TO_CATEGORY_KEY = {
    "Activation/Induction/Causation/Result": "ACTIVATION/INDUCTION/PROMOTION/CAUSATION/RESULT",
    "Repression/Inhibition/Negative Regulation": "REPRESSION/INHIBITION/DECREASE/NEGATIVE REGULATION",
    "Regulation/Control": "REGULATION/CONTROL",
    "Expression/Detection/Identification": "EXPRESSION/DETECTION/IDENTIFICATION",
    "Association/Interaction/Binding": "ASSOCIATION/CORRELATION/RELATION/INTERACTION/BINDING",
    "Localization/Containment/Composition": "LOCALIZATION/CONTAINMENT/COMPOSITION",
    "Requirement/Activity/Function/Participation": "REQUIREMENT/ESSENTIALITY/ACTIVITY/FUNCTION/PARTICIPATION",
    "Encoding": "ENCODING",
    "Synthesis/Formation": "SYNTHESIS/FORMATION"
  };

  /***********************************************************
   * 1) Our standard UI groups
   ***********************************************************/
  const EDGE_GROUPS = [
    "Activation/Induction/Causation/Result",
    "Repression/Inhibition/Negative Regulation",
    "Regulation/Control",
    "Expression/Detection/Identification",
    "Association/Interaction/Binding",
    "Localization/Containment/Composition",
    "Requirement/Activity/Function/Participation",
    "Encoding",
    "Synthesis/Formation"
  ];

  // Which groups are currently selected by the user
  let activeGroups = new Set();
  // A global map of "synonym -> usageCount".
  let synonymUsageMap = {};
  // groupName -> array of synonyms, or the special string 'NO_SYNONYMS'
  const groupSynonymsMap = {};
  // track version for each group to handle in‐flight requests
  const groupToggleVersion = {};

  /***********************************************************
   * 2) Initialize Edge-Group Checkboxes on page load
   ***********************************************************/
  function initializeEdgeGroupCheckboxes() {
    const container = document.getElementById('edgeGroupCheckboxes');
    if (!container) return;

    EDGE_GROUPS.forEach(group => {
      const label = document.createElement('label');
      label.style.display = 'block';
      label.style.margin = '4px 0';

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.value = group;

      checkbox.addEventListener('change', (evt) => {
        toggleEdgeGroup(group, evt.target.checked);
      });

      label.appendChild(checkbox);
      label.appendChild(document.createTextNode(` ${group}`));
      container.appendChild(label);
    });
  }

  /***********************************************************
   * 3) Toggle a Group On/Off  (CHANGED)
   ***********************************************************/
  function toggleEdgeGroup(groupName, isChecked) {
    if (isChecked) {
      activeGroups.add(groupName);

      // If never fetched or "NO_SYNONYMS" or just not an array => attempt fetch once
      if (!fetchedSynonymsForGroup(groupName)) {
        fetchSynonymsForGroup(groupName)
          .then(({ synonyms, outOfDate }) => {
            if (outOfDate) {
              // Distinguish out-of-date from no synonyms:
              console.log(`Semantics-request was cancelled for group: ${groupName}; please allow API to finish loading before toggling checkbox.`);
              return;
            }
            if (!synonyms.length) {
              console.log(`No semantic edges from API for group "${groupName}".`);
              return;
            }
            // We have synonyms => increment usage and refresh checkboxes
            incrementSynonymUsage(synonyms);
            applySynonymUsageToCheckboxes();
          })
          .catch(err => console.error("Error fetching semantics for:", groupName, err));
      } else {
        // We already have them in cache, either an array or 'NO_SYNONYMS'
        const synonyms = getCachedSynonyms(groupName);
        if (!synonyms.length) {
          console.log(`API did not provide semantic edges for group "${groupName}" previously.`);
        } else {
          incrementSynonymUsage(synonyms);
          applySynonymUsageToCheckboxes();
        }
      }
    } else {
      activeGroups.delete(groupName);

      // Mark a new version => any existing in-flight request for this group is invalid
      if (typeof groupToggleVersion[groupName] !== 'number') {
        groupToggleVersion[groupName] = 0;
      }
      groupToggleVersion[groupName]++;

      // Decrement usage for any synonyms we had
      const synonyms = getCachedSynonyms(groupName);
      decrementSynonymUsage(synonyms);
      applySynonymUsageToCheckboxes();
    }
  }

  function fetchedSynonymsForGroup(groupName) {
    return Array.isArray(groupSynonymsMap[groupName]) || groupSynonymsMap[groupName] === 'NO_SYNONYMS';
  }
  function getCachedSynonyms(groupName) {
    return Array.isArray(groupSynonymsMap[groupName]) ? groupSynonymsMap[groupName] : [];
  }

  /***********************************************************
   * 4) Fetch synonyms => return { synonyms, outOfDate } (CHANGED)
   ***********************************************************/
  async function fetchSynonymsForGroup(groupName) {
    console.log("Fetching semantics for group:", groupName);

    // 1) Initialize or bump version for this fetch
    if (typeof groupToggleVersion[groupName] !== 'number') {
      groupToggleVersion[groupName] = 0;
    }
    groupToggleVersion[groupName]++;
    const myVersion = groupToggleVersion[groupName];

    // 2) Gather edgeCounts
    const edgesArray = cy.edges().toArray();
    const edgeCounts = {};
    edgesArray.forEach(edge => {
      const interactionType = edge.data().interaction.toLowerCase();
      if (!edgeCounts[interactionType]) {
        edgeCounts[interactionType] = 0;
      }
      edgeCounts[interactionType]++;
    });

    // 3) Call synonyms API
    let synonymsFromApi = [];
    try {
      const response = await fetch('/openai-edge-synonyms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selectedGroups: [groupName],
          edgeCounts
        })
      });
      if (!response.ok) {
        throw new Error(`Synonyms API Error: ${response.statusText}`);
      }
      const data = await response.json();
      synonymsFromApi = data.semantic_mappings[groupName] || [];
    } catch (err) {
      console.error("Error fetching semantics for:", groupName, err);
      synonymsFromApi = [];
    }

    console.log(`API synonyms for group "${groupName}": ${synonymsFromApi.join(', ')}`);

    // 4) Check if we are still current version => if not, return outOfDate:true
    if (myVersion !== groupToggleVersion[groupName]) {
      return { synonyms: [], outOfDate: true };
    }

    // Merge with static synonyms from CATEGORY_MAPPING
    const categoryKey = GROUP_TO_CATEGORY_KEY[groupName];
    const staticSyns = categoryKey && CATEGORY_MAPPING[categoryKey] ? CATEGORY_MAPPING[categoryKey] : [];
    const combinedSyns = [
      ...synonymsFromApi.map(s => s.toLowerCase()),
      ...staticSyns.map(s => s.toLowerCase())
    ];
    const uniqueSyns = Array.from(new Set(combinedSyns));

    // If final is empty => store "NO_SYNONYMS"
    if (!uniqueSyns.length) {
      console.log(`No synonyms found from API or static for group "${groupName}".`);
      groupSynonymsMap[groupName] = 'NO_SYNONYMS';
      return { synonyms: [], outOfDate: false };
    }

    // Otherwise store them
    groupSynonymsMap[groupName] = uniqueSyns;
    return { synonyms: uniqueSyns, outOfDate: false };
  }

  /***********************************************************
   * 5) Increment/Decrement usage
   ***********************************************************/
  function incrementSynonymUsage(synonyms) {
    synonyms.forEach((syn) => {
      if (typeof synonymUsageMap[syn] === "number") {
        synonymUsageMap[syn]++;
      } else {
        synonymUsageMap[syn] = 1;
      }
    });
  }
  function decrementSynonymUsage(synonyms) {
    synonyms.forEach((syn) => {
      if (typeof synonymUsageMap[syn] === "number") {
        synonymUsageMap[syn]--;
        if (synonymUsageMap[syn] < 0) {
          synonymUsageMap[syn] = 0;
        }
      }
    });
  }

  /***********************************************************
   * 6) Apply usage => check/uncheck edgeType boxes,
   *    then call applyAllFilters().
   ***********************************************************/
  function applySynonymUsageToCheckboxes() {
    const checkboxContainer = document.getElementById('edgeTypeCheckboxes');
    if (!checkboxContainer) return;
  
    Object.keys(synonymUsageMap).forEach((syn) => {
      const usageCount = synonymUsageMap[syn];
      const cb = checkboxContainer.querySelector(`input[type="checkbox"][value="${syn}"]`);
      if (cb) {
        cb.checked = (usageCount > 0);
      }
    });
  
    // Reorder after updating check states
    reorderCheckboxes('edgeTypeCheckboxes');
  
    // Then apply your filter logic
    applyAllFilters();
  }

  /**
   *  Gather node categories that are checked
   */
  function getSelectedNodeCategories() {
    const nodeCategoryCheckboxes = document.querySelectorAll('input[data-category]:checked');
    return new Set(Array.from(nodeCategoryCheckboxes).map(cb => cb.value));
  }

  /**
   *  Gather edge interactions that are checked
   */
  function getSelectedEdgeTypes() {
    const container = document.getElementById('edgeTypeCheckboxes');
    const checkedBoxes = container.querySelectorAll('input[type="checkbox"]:checked');
    const selected = new Set(Array.from(checkedBoxes).map(cb => cb.value));
    return selected;
  }

  /**
   *  Combined filter: node categories + edge types
   */
  function applyAllFilters() {
    cy.startBatch();
  
    // 1) Which node categories are selected?
    const selectedCategories = getSelectedNodeCategories(); 
  
    // 2) Which edge interactions are selected?
    const selectedEdgeTypes = getSelectedEdgeTypes();
  
    // 3) Hide everything first
    cy.nodes().hide();
    cy.edges().hide();
  
    // 4) Show nodes that pass node category OR are query nodes
    cy.nodes().forEach((node) => {
      const nodeCategory = getNodeCategory(node.data('type')?.toLowerCase() || '');
      if (
        selectedCategories.size === 0             // no category selected => show all
        || selectedCategories.has(nodeCategory)   // category is selected
        || isCentralNode(node)                 // always allow query‐term node
      ) {
        node.show();
      }
    });
  
    // 5) Show edges that match edge-type filter and have both endpoints visible
    cy.edges().forEach((edge) => {
      const interaction = edge.data('interaction')?.toLowerCase() || '';
      const edgePasses =
        selectedEdgeTypes.size === 0       // no edge‐type selected => show all
        || selectedEdgeTypes.has(interaction);
  
      if (edgePasses && edge.source().visible() && edge.target().visible()) {
        edge.show();
      }
    });
  
    // 6) Finally, hide any visible node that ends up with no visible edges
    //    unless it's a query node you want to force-display
    cy.nodes(':visible').forEach((node) => {
      const isIsolated = node.connectedEdges(':visible').length === 0;
      if (isIsolated) {
        node.hide();
      }
    });
  
    cy.endBatch();
  
    // Update counters, summaries, etc.
    updateNumNodes();
    updatePaperCount();
    updateNodeSummaries();
  }

  function isQueryNode(nodeId) {
    return queryTerm.some((term) => nodeId.toUpperCase().includes(term));
  }

  /**
   * Original createEdgeFilter logic replaced by dynamic edgeType listing
   */
  function initializeEdgeFilters(batchSize = 200) {
    const checkboxContainer = document.getElementById('edgeTypeCheckboxes');
    const edgesArray = cy.edges().toArray();
    const edgeCounts = {};
    let index = 0;

    function processEdgeBatch() {
      const start = index;
      const end = Math.min(index + batchSize, edgesArray.length);

      for (let i = start; i < end; i++) {
        const edge = edgesArray[i];
        const interactionType = edge.data().interaction.toLowerCase();
        if (!edgeCounts[interactionType]) {
          edgeCounts[interactionType] = 0;
        }
        edgeCounts[interactionType]++;
      }

      index += batchSize;
      if (index < edgesArray.length) {
        requestAnimationFrame(processEdgeBatch);
      } else {
        populateEdgeTypeCheckboxes(edgeCounts, checkboxContainer);
      }
    }
    requestAnimationFrame(processEdgeBatch);
  }

  function populateEdgeTypeCheckboxes(edgeCounts, checkboxContainer, batchSize = 50) {
    const sortedEdgeTypes = Object.keys(edgeCounts).sort((a, b) => edgeCounts[b] - edgeCounts[a]);
    let index = 0;
  
    function processCheckboxBatch() {
      const start = index;
      const end = Math.min(index + batchSize, sortedEdgeTypes.length);
  
      for (let i = start; i < end; i++) {
        const type = sortedEdgeTypes[i];
  
        const label = document.createElement('label');
        label.innerText = `${capitalizeFirstLetter(type)} (${edgeCounts[type]})`;
  
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = type;
        checkbox.setAttribute('data-type', type);
        checkbox.setAttribute('data-count', edgeCounts[type]); // so reorder can read data-count
  
        // On change => reorder and also apply filter
        checkbox.addEventListener('change', () => {
          handleCheckboxChange('edgeTypeCheckboxes');
          applyAllFilters();
        });
  
        label.prepend(checkbox);
        checkboxContainer.appendChild(label);
      }
  
      index += batchSize;
      if (index < sortedEdgeTypes.length) {
        requestAnimationFrame(processCheckboxBatch);
      } else {
        // Once we've appended all labels, reorder them initially:
        reorderCheckboxes('edgeTypeCheckboxes');
      }
    }
    requestAnimationFrame(processCheckboxBatch);
  }

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  /**
   * Node Category Filters
   */
  function initializeCategoryFilters(batchSize = 200) {
    const checkboxContainer = document.getElementById('nodeTypeCheckboxes');
    const categoryCounts = {};
    const nodesArray = cy.nodes().toArray();
    let index = 0;

    function processNodeBatch() {
      const start = index;
      const end = Math.min(index + batchSize, nodesArray.length);

      for (let i = start; i < end; i++) {
        const node = nodesArray[i];
        const type = node.data().type.toLowerCase();
        const category = getNodeCategory(type);

        if (!categoryCounts[category]) {
          categoryCounts[category] = 0;
        }
        categoryCounts[category]++;
      }

      index += batchSize;
      if (index < nodesArray.length) {
        requestAnimationFrame(processNodeBatch);
      } else {
        populateCategoryCheckboxes(categoryCounts, checkboxContainer);
      }
    }
    requestAnimationFrame(processNodeBatch);
  }

  function populateCategoryCheckboxes(categoryCounts, checkboxContainer, batchSize = 50) {
    const sortedCategories = Object.keys(categoryCounts).sort((a, b) => categoryCounts[b] - categoryCounts[a]);
    let index = 0;

    function processCheckboxBatch() {
      const start = index;
      const end = Math.min(index + batchSize, sortedCategories.length);

      for (let i = start; i < end; i++) {
        const category = sortedCategories[i];
        const label = document.createElement('label');
        label.innerText = `${category} (${categoryCounts[category]})`;

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = category;
        checkbox.setAttribute('data-category', category);

        // When user toggles => re‐apply combined filter
        checkbox.addEventListener('change', () => {
          handleCheckboxChange('edgeTypeCheckboxes');  // reorder
          applyAllFilters();
        });

        label.prepend(checkbox);
        checkboxContainer.appendChild(label);
      }

      index += batchSize;
      if (index < sortedCategories.length) {
        requestAnimationFrame(processCheckboxBatch);
      }
    }
    requestAnimationFrame(processCheckboxBatch);
  }

  /**
   * Web worker logic for metrics calculation
   */
  const workerCode = `
    self.onmessage = function (e) {
      try {
        console.log("Worker received data");
        const elements = e.data.elements;
        if (!elements || !Array.isArray(elements.nodes) || !Array.isArray(elements.edges)) {
          throw new Error("Invalid elements: nodes or edges array is missing.");
        }
        console.time("Worker Metrics Calculation Time");
        const result = computeNodeMetrics(elements);
        console.timeEnd("Worker Metrics Calculation Time");
        console.log("Worker finished processing.");
        postMessage(result);
      } catch (err) {
        console.error("Worker error:", err);
        postMessage({ error: err.message });
      }
    };

    function computeNodeMetrics(elements) {
      console.log("Calculating node degrees and clustering coefficients...");
      const degreeMap = {};
      const clusteringMap = {};

      elements.nodes.forEach((node) => {
        degreeMap[node.data.id] = 0;
        clusteringMap[node.data.id] = { neighbors: [] };
      });

      elements.edges.forEach((edge) => {
        const { source, target } = edge.data;
        degreeMap[source] = (degreeMap[source] || 0) + 1;
        degreeMap[target] = (degreeMap[target] || 0) + 1;

        clusteringMap[source].neighbors.push(target);
        clusteringMap[target].neighbors.push(source);
      });

      Object.entries(clusteringMap).forEach(([nodeId, { neighbors }]) => {
        const degree = degreeMap[nodeId];
        if (degree < 2) {
          clusteringMap[nodeId].coefficient = 0;
        } else {
          let connectedNeighbors = 0;
          neighbors.forEach((neighbor, i) => {
            for (let j = i + 1; j < neighbors.length; j++) {
              if (clusteringMap[neighbors[j]].neighbors.includes(neighbor)) {
                connectedNeighbors++;
              }
            }
          });
          clusteringMap[nodeId].coefficient = (2 * connectedNeighbors) / (degree * (degree - 1));
        }
      });

      console.log("Node metrics calculation complete.");
      return { degreeMap, clusteringCoefficients: clusteringMap };
    }
  `;
  const blob = new Blob([workerCode], { type: 'application/javascript' });
  const workerUrl = URL.createObjectURL(blob);
  const layoutWorker = new Worker(workerUrl);
  const numWorkers = navigator.hardwareConcurrency || 24;
  const workers = Array.from({ length: numWorkers }, () => new Worker(workerUrl));
  workers.forEach((worker, index) => {
    worker.onmessage = function (e) {
      if (e.data.error) {
        console.error(`Worker ${index + 1} encountered an error:`, e.data.error);
      } else {
        console.log(`Worker ${index + 1} finished processing:`, e.data);
      }
    };
    worker.onerror = function (err) {
      console.error(`Worker ${index + 1} encountered an error:`, err.message);
    };
  });

  /**
   * Layout logic
   */
  function applyLayout() {
    console.log('Starting layout application...');
    cy.startBatch();
    applyRandomLayoutInBatches();
    cy.endBatch();
  }

  function applyRandomLayoutInBatches(batchSize = 100, graphWidth = 10000, graphHeight = 10000, minSpacing = 50) {
    const nodes = cy.nodes();
    const numBatches = Math.ceil(nodes.length / batchSize);
  
    function processBatch(batchIndex) {
      // If we've processed all batches, finalize the layout.
      if (batchIndex >= numBatches) {
        finalizeRandomLayout();
        return;
      }
  
      // If this is the last batch, include the "deciding layout" message.
      if (batchIndex === numBatches - 1) {
        console.log(`Processing random layout batch ${batchIndex + 1} of ${numBatches}, applying layout based on graph size...`);
      } else {
        console.log(`Processing random layout batch ${batchIndex + 1} of ${numBatches}...`);
      }
  
      const startIndex = batchIndex * batchSize;
      const endIndex = Math.min((batchIndex + 1) * batchSize, nodes.length);
      const nodeBatch = nodes.slice(startIndex, endIndex);
  
      nodeBatch.forEach((node) => {
        let randomX;
        let randomY;
        let isValid = false;
        while (!isValid) {
          randomX = Math.random() * graphWidth;
          randomY = Math.random() * graphHeight;
  
          isValid = !nodes.some((otherNode) => {
            if (node.id() === otherNode.id()) return false;
            const dx = otherNode.position('x') - randomX;
            const dy = otherNode.position('y') - randomY;
            return Math.sqrt(dx * dx + dy * dy) < minSpacing;
          });
        }
        node.position({ x: randomX, y: randomY });
      });
  
      // Schedule the next batch with a minimal delay
      setTimeout(() => processBatch(batchIndex + 1), 0);
    }
  
    processBatch(0);
  }

  function finalizeRandomLayout() {
    const numNodes = cy.nodes().length;

    const layoutOptions = {
      fit: true,
      padding: 50,
    };

    let layout = null;

    if (numNodes <= 1000) {
      console.log('Small graph detected. Applying COSE layout...');
      layout = cy.layout({
        ...layoutOptions,
        name: 'cose',
        animate: true,
        refresh: 4,
        boundingBox: undefined,
        randomize: true,
        debug: false,
        nodeRepulsion: 400000,
        idealEdgeLength: 30,
        edgeElasticity: 50,
        gravity: 100,
        numIter: 100,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
      });
    } else {
      console.log('Large graph detected. FCOSE layout applied.');
      if (numNodes > 2000) {
        layoutOptions.animate = false;
      }
      layout = cy.layout({
        ...layoutOptions,
        name: 'fcose',
        quality: 'default',
        randomize: true,
        nodeRepulsion: () => 4500,
        gravityRangeCompound: 1.5,
        gravity: 0.25,
        edgeElasticity: () => 0.45,
        ...(numNodes <= 2000 ? { idealEdgeLength: () => 400 } : {}),
      });
    }

    layout.run();
    layout.on('layoutready', () => {
      console.log('Layout ready. Adjusting viewport...');
      cy.fit();
    });
    layout.on('layoutstop', () => {
      console.log('Layout completed.');
      cy.fit(cy.elements(), 50);
      cy.center();
    });
    layout.on('layoutstart', () => console.log(`${layout.options.name} layout started...`));
  }

  /**
   * Initialization of the entire application
   */
  function initializeApp() {
    initializeEventListeners();
    // Build checkboxes for edge types (based on actual edges):
    initializeEdgeFilters();
    // Build checkboxes for node categories (based on actual nodes):
    initializeCategoryFilters();
    // Build checkboxes for big "Edge Group" synonyms:
    initializeEdgeGroupCheckboxes();

    applyLayout();
    resetNetworkView();
    showDefinitionsForSearchTerm(queryTerm);
    styleCentralNodes(queryTerm);
    updateNodeSummaries();

    // Let nodes be grabbed if desired
    cy.autoungrabify(false);
  }

  /**
   * On DOM ready, initialize the app
   */
  document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
  });
