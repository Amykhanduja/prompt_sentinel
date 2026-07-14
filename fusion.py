from collections import defaultdict


def fuse_detections(
    regex_detections: list,
    semantic_detections: list
):
    """
    Merge detections from multiple detectors.
    """

    grouped = defaultdict(list)

    for detection in regex_detections:
        grouped[detection["technique"]].append(detection)

    for detection in semantic_detections:
        grouped[detection["technique"]].append(detection)

    fused = []

    for technique, detections in grouped.items():

        result = detections[0].copy()

        result["detectors"] = sorted(
            {
                d["detector"]
                for d in detections
            }
        )

        result["sources"] = sorted(
            {
                d["source"]
                for d in detections
            }
        )

        confidences = [
            d.get(
                "confidence",
                1.0
            )
            for d in detections
        ]

        result["confidence"] = round(
            max(confidences),
            3
        )

        examples = []

        for d in detections:

            if "matched_example" in d:

                examples.append(
                    d["matched_example"]
                )
        result["matched_examples"] = list(dict.fromkeys(examples))
        fused.append(result)

    fused.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    return fused
