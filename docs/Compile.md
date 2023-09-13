# Compile the Windows release from source code

## Easy way to compile

Fork the repository and enable GitHub Actions. Then, go to the Actions tab and click on the latest workflow. Let it run and download the artifacts from the bottom of the page.

## Manual compilation (Windows)


### Prerequisites

Follow the instructions in [Development environment](./Development-env.md) to install all the dependencies.

Then install additional dependencyto compile http-server:

```bash
npm install -g pkg
```


### Compile

Run `BUILD_RELEASE.bat`. The result will be the contents of the `release` folder.
