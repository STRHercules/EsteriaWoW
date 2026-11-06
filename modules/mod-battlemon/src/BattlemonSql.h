#ifndef BATTLEMON_SQL_H
#define BATTLEMON_SQL_H

#include "DatabaseEnv.h"

#include <string>

// AzerothCore's fmt SQL does not quote strings, so a bare {} turns 0025_Pikachu or POKEBALL into a column name
// (MySQL 1054). This returns the surrounding quotes as well as the escaping: pass it straight into a bare {},
// never into '{}'.
inline std::string SqlQuote(std::string s)
{
    CharacterDatabase.EscapeString(s);
    return "'" + s + "'";
}

#endif
