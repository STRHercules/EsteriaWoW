-- Remove strings and commands owned by the previous transmog module.
DELETE FROM `module_string` WHERE `module` = 'mod-transmog';
DELETE FROM `module_string_locale` WHERE `module` = 'mod-transmog';
DELETE FROM `command` WHERE `name` IN (
    'transmog',
    'transmog add',
    'transmog sync',
    'transmog add set',
    'transmog portable',
    'transmog interface',
    'transmog disclaimer',
    'transmog claim',
    'transmog check'
);
