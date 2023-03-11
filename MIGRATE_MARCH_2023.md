# March 2023 update migration info

Hello there! In March 2023, the bot was updated with a system that clearly
separates fluid and non-fluid data files for easier use with services that provide
Docker containers, for example. In addition to this, Docker support was added.

### Migration information

The directory `data/` has now been separated into `fluid_data` (for files that are entirely
fluid (updated as the bot runs) or semi-fluid (includes some configuration and some dynamic content))
and into `static_data` (for data files that are not updated as the bot runs).

To decide what to move, I recommend you to simply look over what is in the `fluid_data` and `static_data` folders in the repository ;)

### New things that this change implemented

- Docker compatibility
- More environment variables for directories which means more possible customization!
- Other functional updates not related to the migration were implemented close to the update.
