# SBRun: tools to run CWL on Seven Bridges powered platforms

This package offers two command line tools `sbpush` and `sbrun` that
push and run CWL tools on any Seven Bridges platform.
 
```
sbpush <cwl> <commit message> <profile> <user> <project> <app_id>
sbpush <cwl> <commit message>
sbpush <cwl>
```

```
sbrun <cwl>
```


`sbpush` uploads a CWL document to a SB platform. `sbrun` runs the CWL
document.

If `<profile> <user> <project> <app_id>` are not supplied, `sbrun` looks
in its cache for them as stored from a previous call. If a task has been
previously run `sbrun` will clone the task and rerun it with the new
version of the app. After pushing or running, the program will attempt
to open a browser at the app or task page.


- `<cwl>` - the path to the CWL file 
- `<commit message>` the commit message you want to appear for the
  revision
- `<profile>` - profile name from your credentials file. For more
  details see below.
- `<user>`, `<project>` - path to project on the platform
- `app_id` - id of the app on the platform



## Credentials file and profiles

If you use the SBG API you already have an API configuration file. If
not, you should create one. It is located in 
`~/.sevenbridges/credentials`.

Briefly, each section in the SBG configuration file (e.g. `[cgc]`) is a 
profile name and has two entries. The end-point and an authentication
token, which you get from your developer tab on the platform.

```
[sbg-us]
api_endpoint = https://api.sbgenomics.com/v2
auth_token   = <dev token here>

[sbg-eu]
api_endpoint = https://eu-api.sbgenomics.com/v2
auth_token   = <dev token here>

[sbg-china]
api_endpoint = https://api.sevenbridges.cn/v2
auth_token   = <dev token here>

[cgc]
api_endpoint = https://cgc-api.sbgenomics.com/v2
auth_token   = <dev token here>

[cavatica]
api_endpoint = https://cavatica-api.sbgenomics.com/v2
auth_token   = <dev token here>
```

You can have several profiles on the same platform if, for example, you 
are an enterprise user and you belong to several divisions. Please refer
to the API documentation for more detail.

## Per app cached information

The `<profile> <project> <app_id>` information and the id of the most
recent test task executed with the app is cached in a file under
`$XDG_DATA_HOME/sevenbridges/sb-run/scratch` (which defaults to
`$HOME/.local/share/sevenbridges/sb-run/scratch`) 
