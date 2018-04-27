# Scripts and codes for running the tools

The Travel Time Matrix tool provides two functionalities Querying and Uploading travel times from and to the database.

##Uploading
To upload travel time matrix data to the data base run the following command:
```
    $ python -m codes --upload -z <./zip_file.zip> -o <./outputFolder>  
```
The zip file must contain CSV files (separated by semicolon ";") with the values that correspond to the columns described in `[ATTRIBUTES_MAPPING]` section in the [configuration file][configuration-file]

##Quarying
To retrieve travel time matrix data from and to different targets run the following command:

```
    $ python -m codes --query -d TO -t 5793265 -o <./outputFolder>  
```

[configuration-file]: resources/configuration.properties