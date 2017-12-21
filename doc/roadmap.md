# Roadmap
The following milestones outline the areas of focus for future mssql-cli work. This document is not intended as a commitment to any 
specific feature or timeline. Instead, the intent is to group related work into milestones using broader themes to convey the direction
and priorities of mssql-cli.  Actual work and focus may change, but the hope is this roadmap is our guide.

## Feedback
The best way to give feedback is to create a github issue in the [dbcli/mssql-cli](https://github.com/dbcli/mssql-cli/issues) repo 
using the [roadmap label](https://github.com/dbcli/mssql-cli/labels/roadmap). 

## Milestone 1
* Parity with pgcli and mycli
  * Support special commands
  * Smart completion
* Engineering Fundamentals
  * Jenkins
  * AppVeyor
  * Code coverage > 80%

## Milestone 2
* Packaging
  * self-contained python runtimes
* Package manager support
  * brew
  * apt-get
  * yum

## Milestone 3
* Non-interactive support
  * Pipe queries via stdin
  * Pipe query results to stdout
  * sqlcmd syntax

## Future Milestones
* Innovation
  * New special commands
    * Script object
    * Script table data
    * Script database
  * Peek definition
  * Schema compare
  * Per database query history
