# idea-libraries-fixer

Script to fix corrupt .idea/libraries directory.

Usage: `python idea-libraries-fixer.py <path-to-idea-directory> <path-to-local-maven-repository>`

## Purpose

Given:
* the latest IntelliJ IDEA community edition (currently 2021.1)
* a Maven-based project
* switching between project branches
* working command-line Maven builds

In IDEA, I get:
* compilation errors referring to missing imports, although the imports are clearly there

Things I tried:
* Maven reimport/reload
* Maven clean command-line builds
* Rebuild project
* Invalidate caches and restart
* Delete .idea directory and recreate project from scratch

The last step worked but I did not want to recreate my project from scratch each time I switched branches, which I end up doing often.  I investigated and found that some of the files in my `.idea/libraries` directory were corrupt.

This directory contains files describing external library sources.  For example, the file `Maven__org_codehaus_groovy_groovy_2_5_14.xml` had this contents:
```xml
<component name="libraryTable">
  <library name="Maven: com.google.code.findbugs:annotations:3.0.1">
    <CLASSES>
      <root url="jar://$MAVEN_REPOSITORY$/com/google/code/findbugs/annotations/3.0.1/annotations-3.0.1.jar!/" />
    </CLASSES>
    <JAVADOC>
      <root url="jar://$MAVEN_REPOSITORY$/com/google/code/findbugs/annotations/3.0.1/annotations-3.0.1-javadoc.jar!/" />
    </JAVADOC>
    <SOURCES>
      <root url="jar://$MAVEN_REPOSITORY$/com/google/code/findbugs/annotations/3.0.1/annotations-3.0.1-sources.jar!/" />
    </SOURCES>
  </library>
</component>
```

Yet the correct contents should be:
```xml
<component name="libraryTable">
  <library name="Maven: org.codehaus.groovy:groovy:2.5.14">
    <CLASSES>
      <root url="jar://$MAVEN_REPOSITORY$/org/codehaus/groovy/groovy/2.5.14/groovy-2.5.14.jar!/" />
    </CLASSES>
    <JAVADOC>
      <root url="jar://$MAVEN_REPOSITORY$/org/codehaus/groovy/groovy/2.5.14/groovy-2.5.14-javadoc.jar!/" />
    </JAVADOC>
    <SOURCES>
      <root url="jar://$MAVEN_REPOSITORY$/org/codehaus/groovy/groovy/2.5.14/groovy-2.5.14-sources.jar!/" />
    </SOURCES>
  </library>
</component>
```

I guess the latest version of IDEA has inadvertently introduced, or exasperated, a concurrency issue resulting in corrupt Maven external library descriptors.  I decided to write a script to correct the problem, until Jetbrains can fix it.

TODO: Add screenshot the next time it happens

## How it works

Terminology:
* descriptor: the fully qualified Maven artifact name, normalized with all separators (path separators, dots, and hyphens) replaced by underscores, just like the file names under the .idea/libraries directory.

The script:
* scans the given local Maven repository
* builds a map of all possible normalized Maven descriptor names, to their corresponding local repository paths
* scans the libraries directory under the given .idea project directory
* finds all files matching `Maven__.*.xml`, extracting the normalized Maven descriptor name
* For each match:
  * find the matching local repository path
  * verify the contents of the file
  * if corrupt, overwrite the file with a generated valid contents

After manually fixing two files, then writing the script and running it, I found seven more corrupt files in my .idea/libraries directory.

## Notes

* the script is a Python script, written with Python2 but should work with Python3 as well since no special features were used.
* it can take a long time to run since it scans the entire given local Maven repository. I tried to do better initially but always hit cases where I could not easily determine the local Maven repository path from the Maven external library descriptor file name.
