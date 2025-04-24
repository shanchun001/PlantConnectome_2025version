from collections import defaultdict

def make_text(elements):
    """
    Optimized text generation for summary display.
    """
    pubmedLink = '<span class="pubmed-link" data-pubmed-id="%s">%s</span>'
    topicDic = defaultdict(lambda: defaultdict(list))
    nodeSentenceDegree = defaultdict(lambda: defaultdict(int))
    nodeDegree = defaultdict(int)

    for i in elements:
        node_id = f"{i.id} [{i.idtype}]"
        target = f"{i.target} [{i.targettype}]"
        topicDic[node_id][i.inter_type].append((target, i.publication))
        nodeSentenceDegree[node_id][i.inter_type] += 1
        nodeDegree[node_id] += 1

    sorted_nodes = sorted(nodeDegree, key=nodeDegree.get, reverse=True)
    save = []

    for node in sorted_nodes:
        for relation in sorted(nodeSentenceDegree[node], key=nodeSentenceDegree[node].get, reverse=True):
            for target, pubmed_id in topicDic[node][relation]:
                pubmed_ref = pubmedLink % (pubmed_id, pubmed_id)
                sentence = (
                    f"<span style='color: #191970;'>{node}</span> "
                    f"<span style='color: #DC143C;'>{relation}</span> "
                    f"<span style='color: #800000;'>{target}</span> "
                    f"(PMID: {pubmed_ref})."
                )
                save.append(f"<div style='padding-bottom: 0.5rem;'>{sentence}</div>")

    return ''.join(save)