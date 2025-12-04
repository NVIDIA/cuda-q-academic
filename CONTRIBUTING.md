Contributing
------------

Please use the following guidelines when contributing to this project. 

Before contributing significant changes, please begin a discussion of the
desired changes via a GitHub Issue to prevent doing unnecessary or overlapping
work.

## License

The preferred license for source code contributed to this project is the Apache
License 2.0 (https://www.apache.org/licenses/LICENSE-2.0) and for
documentation, including Jupyter notebooks and text documentation, is the
Creative Commons Attribution 4.0 International (CC BY-NC 4.0)
(https://creativecommons.org/licenses/by-nc/4.0/deed.en). Contributions under other,
compatible licenses will be considered on a case-by-case basis.

Contributions must include a "signed off by" tag in the commit message for the
contributions asserting the signing of the developers certificate of origin
(https://developercertificate.org/). A GPG-signed commit with the "signed off
by" tag is preferred.

## Styling

Please use the following style guidelines when making contributions.

### Jupyter Notebooks & Markdown

* When they appear inline with the text; directive names, clauses, function or
  subroutine names, variable names, file names, commands and command-line
  arguments should appear between two back ticks.
* Code blocks should begin with three back ticks and end with three back ticks.
* Emphasis, including quotes made for emphasis and introduction of new terms
  should be highlighted between a single pair of asterisks
* A level 1 heading should appear at the top of the notebook as the title of
  the notebook.
.

## Contributing Labs/Modules

A module should have the following directory structure:

* The base of the module should contain a START_HERE file with a brief
  introduction to the module and links to the individual labs for each
  language translation and programming language available.

## Attribution

Portions adopted from https://github.com/OpenACC/openacc-training-materials/blob/master/CONTRIBUTING.md

## Signing Your Work

* We require that all contributors "sign-off" on their commits. This certifies that the contribution is your original work, or you have rights to submit it under the same license, or a compatible license.

  * Any contribution which contains commits that are not Signed-Off will not be accepted.

* To sign off on a commit you simply use the `--signoff` (or `-s`) option when committing your changes:
  ```bash
  $ git commit -s -m "Add cool feature."
  ```
  This will append the following to your commit message:
  ```
  Signed-off-by: Your Name <your@email.com>
  ```

* Full text of the DCO:

  ```
    Developer Certificate of Origin
    Version 1.1
    
    Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
    1 Letterman Drive
    Suite D4700
    San Francisco, CA, 94129
    
    Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.
  ```

  ```
    Developer's Certificate of Origin 1.1
    
    By making a contribution to this project, I certify that:
    
    (a) The contribution was created in whole or in part by me and I have the right to submit it under the open source license indicated in the file; or
    
    (b) The contribution is based upon previous work that, to the best of my knowledge, is covered under an appropriate open source license and I have the right under that license to submit that work with modifications, whether created in whole or in part by me, under the same open source license (unless I am permitted to submit under a different license), as indicated in the file; or
    
    (c) The contribution was provided directly to me by some other person who certified (a), (b) or (c) and I have not modified it.
    
    (d) I understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information I submit with it, including my sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.
  ```