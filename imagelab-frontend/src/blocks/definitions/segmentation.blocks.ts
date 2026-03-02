export const segmentationBlocks = [
  {
    type: "segmentation_watershed",
    message0: "Watershed Segmentation %1 Foreground Threshold %2",
    args0: [
      { type: "input_dummy" },
      {
        type: "field_number",
        name: "foreground_threshold",
        value: 0.5,
        min: 0.1,
        max: 0.9,
        precision: 0.1,
      },
    ],
    previousStatement: null,
    nextStatement: null,
    style: "segmentation_style",
    tooltip:
      "Applies watershed segmentation - A classical algorithm that treats the image like a topographic map, flooding basins from marker points to separate distinct regions. The foreground threshold (0.1–0.9) controls how confidently a region must stand out to be treated as foreground. Segment boundaries are highlighted in red. Useful for separating touching or overlapping objects in an image.",
  },
  {
    type: "segmentation_kmeans",
    message0:
      "K-Means Segmentation %1 Number of clusters (K) %2 %3 Max iterations %4 %5 Epsilon %6",
    args0: [
      { type: "input_dummy" },
      { type: "field_number", name: "k", value: 3, min: 2, max: 10 },
      { type: "input_dummy" },
      { type: "field_number", name: "max_iter", value: 100, min: 1 },
      { type: "input_dummy" },
      { type: "field_number", name: "epsilon", value: 0.2, min: 0.01, precision: 0.01 },
    ],
    previousStatement: null,
    nextStatement: null,
    style: "segmentation_style",
    tooltip:
      "Applies K-Means color segmentation - Groups pixels into K clusters based on color similarity, replacing each pixel with the average color of its cluster. K controls the number of color segments (2–10). Higher K values produce more detailed segmentation. Max iterations and epsilon control the convergence of the algorithm. Great for simplifying images and understanding dominant color regions.",
  },
];
