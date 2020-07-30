# A Methodical Approach to the Evaluation of Light Transport Computations
Photorealistic rendering has a wide variety of applications, and so there are many rendering algorithms and their variations tailored for specific use cases. Even though practically all of them do physically-based simulations of light transport, their results on the same scene are often different - sometimes because of the nature of a given algorithm or in a worse case because of bugs in their implementation. It is difficult to compare these algorithms, especially across different rendering frameworks, because there is not any standardized testing software or dataset available. Therefore, the only way to get an unbiased comparison of algorithms is to create and use your dataset or reimplement the algorithms in one rendering framework of choice, but both solutions can be difficult and time-consuming. We address these problems with our test suite based on a rigorously defined methodology of evaluation of light transport algorithms. We present a scripting framework for automated testing and fast comparison of rendering results and provide a documented set of non-volumetric test scenes for most popular research-oriented rendering frameworks. Our test suite is easily extensible to support additional renderers and scenes.

See "A Methodical Approach to the Evaluation of Light Transport Computations.pdf" for detailed documentation.

See configurations folder for examples of input files of the `lteval.py` script.

Current version of the evaluation framework is available at https://github.com/tazlarv/lteval.
