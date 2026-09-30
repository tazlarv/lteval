# A Methodical Approach to the Evaluation of Light Transport Computations

<img width="100%" alt="combined-image (1)" src="https://github.com/user-attachments/assets/7d5e74f5-201f-43fa-bc53-95b1cf138afe" />

## About

Master's thesis · Charles University, Faculty of Mathematics and Physics · 2020  

This repository contains:
- [**Complete thesis (PDF)**](A%20Methodical%20Approach%20to%20the%20Evaluation%20of%20Light%20Transport%20Computations.pdf) — the full text of the thesis, including the technical documentation
- **Implementation** developed as part of the thesis
- [**Configurations**](configurations) folder with example input files for the main `lteval.py` script

The thesis, together with all related files and documents, is also available in the official [Charles University digital repository](https://dspace.cuni.cz/handle/20.500.11956/121321).

## Abstract
Photorealistic rendering has a wide variety of applications, and so there are many rendering algorithms and their variations tailored for specific use cases. Even though practically all of them do physically-based simulations of light transport, their results on the same scene are often different - sometimes because of the nature of a given algorithm or in a worse case because of bugs in their implementation. It is difficult to compare these algorithms, especially across different rendering frameworks, because there is not any standardized testing software or dataset available. Therefore, the only way to get an unbiased comparison of algorithms is to create and use your dataset or reimplement the algorithms in one rendering framework of choice, but both solutions can be difficult and time-consuming. We address these problems with our test suite based on a rigorously defined methodology of evaluation of light transport algorithms. We present a scripting framework for automated testing and fast comparison of rendering results and provide a documented set of non-volumetric test scenes for most popular research-oriented rendering frameworks. Our test suite is easily extensible to support additional renderers and scenes.

## Licenses

The original code in this repository is licensed under the MIT License.
See [LICENSE](LICENSE).

This repository also contains or redistributes third-party software - namely: 
- Mitsuba (0.5) renderer
- PBRT (3) renderer
- JERI (JavaScript Extended Range ImageViewer)

Those components remain subject to their respective licenses.
See [data/renderers](data/renderers) and [data/jeri](data/jeri) for details.
