-- ============================================================================
-- Autora: Noa
-- ============================================================================
-- Contiene las estructuras de datos para las razas y clases del juego

--ES
local Races_Informations = {

[16] = {
      Name = "Eredar",
      Description = "Eredar are the ancient, fel-touched draenei who wield immense arcane and demonic power.",
};

[17] = {
      Name = "Nightborne",
      Description = "Nightborne are the children of Suramar, steeped in the Nightwell and its arcane gifts.",
};

[19] = {
      Name = "Void Elf",
      Description = "Void elves channel the shadow between the stars, wielding entropy as a weapon.",
};

[21] = {
      Name = "Lightforged Draenei",
      Description = "Lightforged draenei are infused with the Light, forged to wage the eternal war against the Legion.",
};

[22] = {
      Name = "Zandalari Troll",
      Description = "Zandalari trolls are the proud, ancient forebears of all trollkind, blessed by their loa.",
};

[23] = {
      Name = "Dark Iron Dwarf",
      Description = "Dark Iron dwarves are born of the fire beneath Blackrock, hardened and fiercely independent.",
};

[28] = {
      Name = "Dracthyr",
      Description = "Dracthyr are ancient draconic soldiers, wielding the magic of all five dragonflights.",
};

[29] = {
      Name = "Kul Tiran",
      Description = "Kul Tirans are the hardy seafarers of Boralus, steeped in the tides and old ways of Drustvar.",
};

[30] = {
      Name = "Illidari",
      Description = "Illidari are demon hunters who bound themselves to fel power to hunt the Burning Legion.",
};

[1] = {
      Name = "Humano",
      Description = "Los humanos son una raza joven y, por lo tanto, muy versátil. Dominan las artes del combate, la artesanía y la magia con una eficacia sorprendente. Su valor y optimismo los han llevado a levantar algunos de los reinos más espléndidos del mundo. En esta turbulenta era, tras generaciones de conflictos, los humanos quieren recuperar la gloria que los distinguió otrora y forjarse un nuevo y brillante futuro.",
      Spell_1 = {name = "Cada Hombre por Sí Mismo", icon = "spell_shadow_charm", description = "Elimina todos los efectos que impiden el movimiento y todos los efectos que provocan pérdida de control de tu personaje."},
      Spell_2 = {name = "Especialización con Espadas", icon = "ability_meleedamage", description = "La pericia con Espadas y Espadas de Dos Manos aumenta en 3."},
      Spell_3 = {name = "Especialización con Mazas", icon = "inv_hammer_05", description = "La pericia con Mazas y Mazas de Dos Manos aumenta en 3."},
      Spell_4 = {name = "El Espíritu Humano", icon = "inv_enchant_shardbrilliantsmall", description = "Espíritu aumentado en un 3%."},
      Spell_5 = {name = "Percepción", icon = "spell_nature_sleep", description = "Aumenta tu detección de Sigilo."},
      Spell_6 = {name = "Diplomacia", icon = "inv_misc_note_02", description = "La ganancia de reputación aumenta en un 10%."},
     },
[2] = {
      Name = "Enano",
      Description = "En el pasado, los enanos solo se preocupaban por las riquezas extraídas de las entrañas de la tierra. Fue así como hallaron vestigios de una raza divina que, según parece, les dio vida... y derecho de nacimiento encantado. Impulsados a aprender más por este descubrimiento, los enanos se consagraron a la búsqueda de artefactos perdidos y el conocimiento arcano. Hoy en día, hay arqueólogos enanos repartidos por todo el mundo.",
      Spell_1 = {name = "Especialización con Mazas", icon = "inv_hammer_05", description = "La pericia con Mazas y Mazas de Dos Manos aumenta en 5."},
      Spell_2 = {name = "Forma de Piedra", icon = "spell_shadow_unholystrength", description = "Elimina todos los efectos de veneno, enfermedad y sangrado, además aumenta tu armadura en un 10% durante 0.1 segundos."},
      Spell_3 = {name = "Especialización con Armas de Fuego", icon = "inv_musket_03", description = "Tu probabilidad de golpe crítico con Armas de Fuego aumenta en un 1%."},
      Spell_4 = {name = "Resistencia a la Escarcha", icon = "spell_frost_wizardmark", description = "Reduce la probabilidad de ser alcanzado por hechizos de Escarcha en un 2%."},
      Spell_5 = {name = "Detectar Tesoro", icon = "racial_dwarf_findtreasure", description = "Permite al enano percibir tesoros cercanos, mostrándolos en el minimapa. Dura hasta cancelación."},
     },
[3] = {
      Name = "Elfo de la Noche",
      Description = "Hace diez mil años, los elfos de la noche fundaron un vasto imperio, pero el uso imprudente de la magia primaria los llevó a la ruina. Consternados, se retiraron a los bosques donde se aislaron hasta el regreso de su antiguo enemigo: la Legión Ardiente. Entonces no tuvieron más opción que abandonar su reclusión y luchar por su lugar en el nuevo mundo.",
      Spell_1 = {name = "Fusión en las Sombras", icon = "ability_ambush", description = "Actívalo para deslizarte en las sombras, reduciendo la probabilidad de ser detectado por los enemigos. Dura hasta ser cancelado o al moverte. Al cancelarse, toda la amenaza se restaura contra enemigos aún en combate."},
      Spell_2 = {name = "Elusividad", icon = "ability_racial_ultravision", description = "Reduce la probabilidad de ser detectado mientras estás en Sigilo o en Fusión en las Sombras."},
      Spell_3 = {name = "Resistencia a la Naturaleza", icon = "spell_nature_spiritarmor", description = "Reduce la probabilidad de ser alcanzado por hechizos de Naturaleza en un 2%."},
      Spell_4 = {name = "Presteza", icon = "ability_racial_shadowmeld", description = "Reduce en un 2% la probabilidad de ser alcanzado por ataques cuerpo a cuerpo y a distancia."},
      Spell_5 = {name = "Espíritu de Fuego Fatuo", icon = "spell_nature_wispsplode", description = "Te transformas en un fuego fatuo al morir, aumentando tu velocidad en un 75%."},
     },
[4] = {
      Name = "Gnomo",
      Description = "A pesar de su baja estatura, los gnomos de Khaz Modan usaron su prodigioso intelecto para asegurarse un lugar en la Historia. Sin ninguna duda, su reino subterráneo, Gnomeregan, era una maravilla de la tecnología a vapor. Pero así y todo, perdieron la ciudad durante una invasión masiva de troggs. Ahora, los creadores de esta maravilla vagan por las tierras de los enanos, ayudándoles lo mejor que pueden.",
      Spell_1 = {name = "Artista del Escape", icon = "ability_rogue_trip", description = "Escapas de cualquier efecto que te inmovilice o reduzca tu velocidad de movimiento."},
      Spell_2 = {name = "Resistencia Arcana", icon = "spell_nature_wispsplode", description = "Reduce la probabilidad de ser alcanzado por hechizos Arcanos en un 2%."},
      Spell_3 = {name = "Mente Expansiva", icon = "inv_enchant_essenceeternallarge", description = "Intelecto aumentado en un 5%."},
      Spell_4 = {name = "Especialización en Ingeniería", icon = "inv_misc_gear_01", description = "Habilidad en Ingeniería aumentada en 15."},
     },
[5] = {
      Name = "Draenei",
      Description = "Lejos de su hogar, Argus, los honorables draenei huyeron de la Legión Ardiente durante eones antes de encontrar un planeta remoto donde asentarse. Compartieron ese mundo con los chamanísticos orcos y lo llamaron Draenor. Con el tiempo, la Legión corrompió a los orcos, quienes hicieron la guerra y casi exterminaron a los pacíficos draenei. Unos pocos afortunados escaparon y llegaron a Azeroth donde ahora buscan aliados en su batalla contra la Legión Ardiente.",
      Spell_1 = {name = "Don de los Naaru", icon = "spell_holy_holyprotection", description = "Sana al objetivo durante 15 seg. La cantidad de sanación aumenta con tu poder de ataque."},
      Spell_2 = {name = "Tallado de Gemas", icon = "spell_misc_conjuremanajewel", description = "Habilidad en Joyería aumentada en 5."},
      Spell_3 = {name = "Presencia Heroica", icon = "inv_helmet_21", description = "Aumenta la probabilidad de acierto con todos los ataques y hechizos en un 1% para ti y todos los miembros de tu grupo en un radio de 30 m."},
      Spell_4 = {name = "Resistencia a las Sombras", icon = "spell_shadow_detectinvisibility", description = "Reduce la probabilidad de ser alcanzado por hechizos de Sombras en un 2%."},
     },
[6] = {
      Name = "Orco",
      Description = "La raza de los orcos es originaria del planeta Draenor. Este pueblo pacífico, de creencias chamánicas, fue esclavizado por la Legión Ardiente y forzado a participar en la guerra contra los humanos de Azeroth. Aunque tuvieron que pasar muchos años, al final escaparon de la corrupción de los demonios y recuperaron su libertad. A día de hoy, luchan por su honor en un mundo que los odia y desprecia.",
      Spell_1 = {name = "Furia Sangrienta", icon = "racial_orc_berserkerstrength", description = "Aumenta el poder de ataque en un 6%. Dura 15 seg."},
      Spell_2 = {name = "Mando", icon = "ability_warrior_warcry", description = "El daño infligido por las mascotas aumenta en un 5%."},
      Spell_3 = {name = "Dureza", icon = "inv_helmet_23", description = "La duración de los aturdimientos se reduce un 15% adicional."},
      Spell_4 = {name = "Especialización con Hachas", icon = "inv_axe_02", description = "La pericia con Armas de Puño, Hachas y Hachas de Dos Manos aumenta en 5."},
     },
[7] = {
      Name = "No Muerto",
      Description = "Fuera del alcance del Rey Exánime, los Renegados buscan la manera de derrocarlo. El alma en pena Sylvanas lidera su sed de venganza contra la Plaga. Los humanos ahora también son el enemigo, implacables en su intento de purgar de no-muertos el mundo. A los Renegados les importan poco incluso sus aliados; para ellos, la Horda no es más que una herramienta para promover sus oscuros planes.",
      Spell_1 = {name = "Canibalismo", icon = "ability_racial_cannibalize", description = "Al activarse, regenera un 7% de la salud total cada 2 seg durante 10 seg. Solo funciona con cadáveres humanoides o no muertos a 5 m."},
      Spell_2 = {name = "Voluntad de los Renegados", icon = "spell_shadow_raisedead", description = "Elimina cualquier efecto de Encantamiento, Miedo o Sueño. Este efecto comparte un tiempo de reutilización de 45 seg con otros similares."},
      Spell_3 = {name = "Resistencia a las Sombras", icon = "spell_shadow_detectinvisibility", description = "Reduce la probabilidad de ser alcanzado por hechizos de Sombras en un 2%."},
      Spell_4 = {name = "Respiración Subacuática", icon = "spell_shadow_demonbreath", description = "La duración de la respiración bajo el agua aumenta un 233%."},
     },
[8] = {
      Name = "Tauren",
      Description = "Los tauren se esfuerzan continuamente para preservar el equilibrio de la Naturaleza y respetar los deseos de la diosa que veneran, la Madre Tierra. Hace poco fueron atacados por mortíferos centauros y habrían sido aniquilados si no hubiese sido por un encuentro fortuito con los orcos, que les ayudaron a derrotar a los intrusos. Para hacer honor a esta deuda de sangre, los tauren se unieron a la Horda, afianzando la amistad de ambas razas.",
      Spell_1 = {name = "Pisotón de Guerra", icon = "ability_warstomp", description = "Aturde hasta 5 enemigos en un radio de 8 m durante 2 seg."},
      Spell_2 = {name = "Resistencia", icon = "spell_nature_unyeildingstamina", description = "La salud base aumenta en un 5%."},
      Spell_3 = {name = "Resistencia a la Naturaleza", icon = "spell_nature_spiritarmor", description = "Reduce la probabilidad de ser alcanzado por hechizos de Naturaleza en un 2%."},
      Spell_4 = {name = "Cultivo", icon = "inv_misc_flower_01", description = "Habilidad en Herboristería aumentada en 15."},
     },
[9] = {
      Name = "Trol",
      Description = "Los fieros trols de la tribu Lanza Negra habitaban las junglas de la Vega de Tuercespina hasta que facciones guerreras los expulsaron de allí. Con el tiempo, los trols entablaron amistad con la Horda de los orcos y Thrall, el joven Jefe de Guerra orco, los convenció para que viajasen con él a Kalimdor. A pesar de su inherente herencia oscura, los trols de la tribu Lanza Negra ocupan un lugar privilegiado en la Horda.",
      Spell_1 = {name = "Rabiar", icon = "racial_troll_berserk", description = "Aumenta tu velocidad de ataque y lanzamiento en un 20% durante 10 seg."},
      Spell_2 = {name = "Regeneración", icon = "spell_nature_regenerate", description = "La tasa de regeneración de salud aumenta en un 10%. El 10% de la regeneración total continúa durante el combate."},
      Spell_3 = {name = "Asesino de Bestias", icon = "inv_misc_pelt_bear_ruin_02", description = "El daño infligido contra Bestias aumenta en un 5%."},
      Spell_4 = {name = "Especialización en Armas Arrojadizas", icon = "inv_throwingaxe_03", description = "Tu probabilidad de golpe crítico con armas arrojadizas aumenta en un 1%."},
      Spell_5 = {name = "Especialización con Arcos", icon = "inv_weapon_bow_12", description = "Tu probabilidad de golpe crítico con Arcos aumenta en un 1%."},
      Spell_6 = {name = "El Vudú Zalamero", icon = "inv_misc_idol_02", description = "Reduce la duración de todos los efectos que impiden el movimiento en un 15%. ¡Los trolls siempre se escapan, mon!"},
     },
[10] = {
      Name = "Elfo de Sangre",
      Description = "Hace mucho tiempo, los elfos nobles exiliados fundaron Quel'Thalas y allí crearon una fuente mágica, La Fuente del Sol. A pesar de que sus poderes los fortalecieron, desarrollaron una fuerte adicción a ellos.\n\nAños más tarde, la Plaga de los no-muertos destruyó La Fuente del Sol y casi la totalidad de la población de elfos nobles. Ahora, conocidos como los elfos de sangre, estos refugiados dispersos intentan reconstruir Quel'Thalas a la par que buscan una nueva fuente mágica que calme su dolorosa adicción.",
      Spell_1 = {name = "Torrente Arcano", icon = "spell_shadow_teleport", description = "Silencia a todos los enemigos en un radio de 8 m durante 2 seg y restaura un 6% de tu maná. Además, interrumpe el lanzamiento de hechizos de objetivos que no sean jugadores durante 3 seg."},
      Spell_2 = {name = "Afinidad Arcana", icon = "inv_enchant_shardglimmeringlarge", description = "Habilidad en Encantamiento aumentada en 10."},
      Spell_3 = {name = "Resistencia Mágica", icon = "spell_shadow_antimagicshell", description = "Reduce la probabilidad de ser alcanzado por hechizos en un 2%."},
     },
}

local standardRaceInfo = {
    [8] = Races_Informations[6],
    [9] = Races_Informations[7],
    [10] = Races_Informations[8],
    [11] = Races_Informations[9],
    [12] = Races_Informations[10],
}

Races_Informations[6] = {
    Name = "Worgen",
    Description = "The curse of Gilneas transformed its people into worgen, formidable beasts who now fight to reclaim their humanity.",
    Spell_1 = {name = "Aberration", icon = "spell_nature_nature_resist", description = "Reduces the chance to be hit by Nature and Shadow spells."},
    Spell_2 = {name = "Two Forms", icon = "ability_racial_twoforms", description = "Switches between human and worgen form."},
    Spell_3 = {name = "Running Wild", icon = "ability_druid_dash", description = "Drops to all fours and runs as fast as a wild animal."},
}
Races_Informations[7] = {
    Name = "High Elf",
    Description = "High elves preserve their ancient traditions and pursue balance after refusing the path taken by most of their former kin.",
    Spell_1 = {name = "Arcane Affinity", icon = "spell_holy_mindvision", description = "May restore mana, energy, runic power, or rage."},
    Spell_2 = {name = "Arcane Acuity", icon = "spell_shadow_charm", description = "Agility increased by 2%."},
    Spell_3 = {name = "Bow Specialization", icon = "inv_weapon_bow_07", description = "Increased critical chance with Bows."},
    Spell_4 = {name = "Enchanting", icon = "trade_engraving", description = "Enchanting skill increased."},
}
Races_Informations[8] = standardRaceInfo[8]
Races_Informations[9] = standardRaceInfo[9]
Races_Informations[10] = standardRaceInfo[10]
Races_Informations[11] = standardRaceInfo[11]
Races_Informations[12] = {
    Name = "Goblin",
    Description = "Clever and resourceful, goblins turn invention, commerce, and explosives into weapons of survival.",
    Spell_1 = {name = "Best Deals Anywhere", icon = "inv_misc_coin_08", description = "Always receives the best possible gold discount."},
    Spell_2 = {name = "Rocket Barrage", icon = "ability_hunter_misdirection", description = "Launches belt rockets at an enemy, dealing fire damage."},
    Spell_3 = {name = "Rocket Jump", icon = "ability_rogue_bladetwisting", description = "Activates the rocket belt to jump forward."},
    Spell_4 = {name = "Time is Money", icon = "ability_rogue_sprint", description = "Attack and casting speed increased by 1%."},
}
Races_Informations[13] = standardRaceInfo[12]
Races_Informations[14] = {
    Name = "Mag'har Orc",
    Description = "The uncorrupted orc clans of Draenor fight with pride, courage, and an unrelenting sense of honor.",
    Spell_1 = {name = "Ancestral Call", icon = "spell_nature_ancestralguardian", description = "Calls on your uncorrupted ancestors to increase attack power and spell damage."},
    Spell_2 = {name = "Savage Blood", icon = "racial_orc_command", description = "Grants a chance to resist Curse, Disease, and Poison effects."},
    Spell_3 = {name = "Sympathetic Vigor", icon = "ability_hunter_beastcall", description = "Increases your pet's maximum health."},
    Spell_4 = {name = "Unwavering Will", icon = "inv_helmet_23", description = "Reduces the duration of Stun effects."},
}
Races_Informations[15] = {
    Name = "Sethrak",
    Description = "Cunning champions of the sands, the Sethrak wield elemental magic and ancient secrets against their enemies.",
    Spell_1 = {name = "Sandswept", icon = "spell_nature_earthquake", description = "Resistant to Nature damage."},
    Spell_2 = {name = "Desert Mastery", icon = "spell_shadow_shadowfiend", description = "Increased mastery of desert survival."},
}

local goblinInfo = Races_Informations[12]
local bloodElfInfo = Races_Informations[13]
local eredarInfo = Races_Informations[16]
local nightborneInfo = Races_Informations[17]
local magharInfo = Races_Informations[14]
local sethrakInfo = Races_Informations[15]
local brokenInfo = {
    Name = "Broken",
    Description = "Broken draenei survive through ingenuity, stealth, and an unbroken connection to the Naaru.",
    Spell_1 = {name = "Salvager", icon = "trade_engineering", description = "Engineering and Mining skill increased by 10, and repair costs reduced by 10%."},
    Spell_2 = {name = "Krokul Cunning", icon = "ability_hunter_misdirection", description = "Reduces the radius at which enemies detect you by 5 yards."},
    Spell_3 = {name = "Fel-Scarred", icon = "spell_shadow_antimagicshell", description = "Magic effects that would drain your mana are 10% less effective, and Shadow resistance increased by 10."},
    Spell_4 = {name = "Echo of the Naaru", icon = "spell_holy_holyprotection", description = "Restore 15% maximum health over 10 seconds. 3 minute cooldown."},
}
Races_Informations[8] = sethrakInfo
Races_Informations[9] = standardRaceInfo[8]
Races_Informations[10] = standardRaceInfo[9]
Races_Informations[11] = standardRaceInfo[10]
Races_Informations[12] = standardRaceInfo[11]
Races_Informations[13] = goblinInfo
Races_Informations[14] = bloodElfInfo
Races_Informations[15] = magharInfo
Races_Informations[14] = brokenInfo
Races_Informations[16] = { Name = "Pandaren", Description = "Disciplined and resilient people of the mists." }
Races_Informations[17] = { Name = "Vulpera", Description = "Resourceful desert survivors and clever allies." }
Races_Informations[18] = { Name = "Darkfallen", Description = "Children of the night, bound by shadow and blood." }
Races_Informations[19] = { Name = "Void Elf", Description = _G.RACE_INFO_VOIDELF or "Shadow-touched elves who wield the Void from Telogrus Rift." }

local raceInfoByFileString = {
    HUMAN = Races_Informations[1],
    DWARF = Races_Informations[2],
    NIGHTELF = Races_Informations[3],
    GNOME = Races_Informations[4],
    DRAENEI = Races_Informations[5],
    WORGEN = Races_Informations[6],
    HIGHELF = Races_Informations[7],
    SETHRAK = Races_Informations[8],
    ORC = Races_Informations[9],
    SCOURGE = Races_Informations[10],
    TAUREN = Races_Informations[11],
    TROLL = Races_Informations[12],
    GOBLIN = Races_Informations[13],
    BROKEN = Races_Informations[14],
    MAGHAR = Races_Informations[15],
    PANDAREN = Races_Informations[16],
    VULPERA = Races_Informations[17],
    DARKFALLEN = Races_Informations[18],
    DARKFALLENHORDE = Races_Informations[18],
    BLOODELF = bloodElfInfo,
    SKYBORNE = bloodElfInfo,
    SKYBORNEHORDE = bloodElfInfo,
    EREDAR = eredarInfo,
    NIGHTBORNE = nightborneInfo,
    VOIDELF = Races_Informations[19],
    LIGHTFORGEDDRAENEI = Races_Informations[21],
    ZANDALARITROLL = Races_Informations[22],
    DARKIRONDWARF = Races_Informations[23],
    DRACTHYR = Races_Informations[28],
    KULTIRAN = Races_Informations[29],
    ILLIDARI = Races_Informations[30],
}

local Class_Informations = {
[1] = {
      Name = "Guerrero",
      Description = "Los guerreros son los maestros del combate cuerpo a cuerpo, capaces de usar una gran variedad de armas y armaduras. Su fuerza y resistencia los convierten en tanques formidables, capaces de proteger a sus aliados mientras infligen daño devastador a sus enemigos.",
      Roles = "Daño cuerpo a cuerpo, Tanque.",
     },
[2] = {
      Name = "Paladín",
      Description = "Los paladines son guerreros sagrados que combinan el combate cuerpo a cuerpo con la magia divina. Dedicados a la justicia y la protección de los inocentes, pueden sanar aliados, protegerlos con bendiciones y castigar a los malvados con poder sagrado.",
      Roles = "Daño cuerpo a cuerpo, Tanque, Sanador.",
     },
[3] = {
      Name = "Cazador",
      Description = "Los cazadores son maestros del combate a distancia y la supervivencia en la naturaleza. Acompañados por sus fieles compañeros animales, pueden rastrear enemigos, tender trampas y atacar desde la distancia con arcos y armas de fuego.",
      Roles = "Daño a distancia.",
     },
[4] = {
      Name = "Pícaro",
      Description = "Los pícaros son maestros del sigilo y el engaño, capaces de moverse sin ser detectados y atacar desde las sombras. Su agilidad y destreza les permiten infligir daño crítico letal, mientras evitan los ataques enemigos con movimientos ágiles.",
      Roles = "Daño cuerpo a cuerpo.",
     },
[5] = {
      Name = "Sacerdote",
      Description = "Los sacerdotes son maestros de la magia divina, dedicados a sanar y proteger a sus aliados. Aunque también pueden canalizar poderes sombríos, su verdadera fuerza radica en su capacidad para restaurar la vida y brindar protección espiritual.",
      Roles = "Daño a distancia, Sanador.",
     },
[6] = {
      Name = "Caballero de la Muerte",
      Description = "Los caballeros de la muerte son guerreros no muertos que han dominado las artes necrománticas. Una vez sirvientes del Rey Exánime, ahora luchan con su propia voluntad, combinando habilidades marciales con magia sombría y poderes sobre la muerte.",
      Roles = "Daño cuerpo a cuerpo, Tanque.",
      },
[7] = {
      Name = "Chamán",
      Description = "Los chamanes son intermediarios entre el mundo espiritual y el físico, capaces de canalizar los elementos y comunicarse con los espíritus. Pueden sanar a sus aliados, invocar tótems poderosos y desatar la furia de los elementos sobre sus enemigos.",
      Roles = "Daño cuerpo a cuerpo, Daño a distancia, Sanador.",
      },
[8] = {
      Name = "Mago",
      Description = "Los magos son maestros de las artes arcanas, capaces de canalizar poderosos hechizos elementales. Aunque frágiles físicamente, su dominio de la magia los convierte en una fuerza devastadora en el campo de batalla, capaces de controlar el hielo, el fuego y las fuerzas arcanas.",
      Roles = "Daño a distancia.",
      },
[9] = {
      Name = "Brujo",
      Description = "Los brujos han hecho pactos con fuerzas demoníacas para obtener poder. Maestros de la magia sombría y vil, pueden invocar demonios, drenar la vida de sus enemigos y canalizar energías corruptoras para devastar el campo de batalla.",
      Roles = "Daño a distancia.",
      },
[10] = {
      Name = "Druida",
      Description = "Los druidas son guardianes de la naturaleza, capaces de transformarse en diferentes formas animales. Su versatilidad les permite cumplir múltiples roles: pueden sanar como sacerdotes, tanquear como guerreros, o infligir daño como magos, todo mientras mantienen su conexión con el mundo natural.",
      Roles = "Daño cuerpo a cuerpo, Daño a distancia, Tanque, Sanador.",
      },
};

local RaceTooltipPositions = {
    Alliance = {
        [1] = { -- Humano
            high = {point = "TOPLEFT", relPoint = "TOPRIGHT", x = 20, y = 20},
            low = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -80},
            veryLow = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -180},
            default = {point = "LEFT", relPoint = "RIGHT", x = 20, y = 0}
        },
        [2] = { -- Enano
            high = {point = "TOPLEFT", relPoint = "TOPRIGHT", x = 20, y = 40},
            low = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -60},
            veryLow = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -140},
            default = {point = "LEFT", relPoint = "RIGHT", x = 20, y = 20}
        },
        [3] = { -- Elfo de la noche
            high = {point = "TOPLEFT", relPoint = "TOPRIGHT", x = 20, y = 20},
            low = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -80},
            veryLow = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -180},
            default = {point = "LEFT", relPoint = "RIGHT", x = 20, y = 0}
        },
        [4] = { -- Gnomo
            high = {point = "TOPLEFT", relPoint = "TOPRIGHT", x = 20, y = 40},
            low = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -60},
            veryLow = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -140},
            default = {point = "LEFT", relPoint = "RIGHT", x = 20, y = 20}
        },
        [5] = { -- Draenei
            high = {point = "TOPLEFT", relPoint = "TOPRIGHT", x = 20, y = 20},
            low = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -80},
            veryLow = {point = "BOTTOMLEFT", relPoint = "TOPRIGHT", x = 20, y = -180},
            default = {point = "LEFT", relPoint = "RIGHT", x = 20, y = 0}
        }
    },
    Horde = {
        [6] = { -- Orco
            high = {point = "TOPRIGHT", relPoint = "TOPLEFT", x = -20, y = 20},
            veryLow = {point = "BOTTOMRIGHT", relPoint = "TOPLEFT", x = -20, y = -120},
            default = {point = "RIGHT", relPoint = "LEFT", x = -20, y = 0}
        },
        [7] = { -- No-muerto
            high = {point = "TOPRIGHT", relPoint = "TOPLEFT", x = -20, y = 40},
            veryLow = {point = "BOTTOMRIGHT", relPoint = "TOPLEFT", x = -20, y = -80},
            default = {point = "RIGHT", relPoint = "LEFT", x = -20, y = 20}
        },
        [8] = { -- Tauren
            high = {point = "TOPRIGHT", relPoint = "TOPLEFT", x = -20, y = 20},
            veryLow = {point = "BOTTOMRIGHT", relPoint = "TOPLEFT", x = -20, y = -120},
            default = {point = "RIGHT", relPoint = "LEFT", x = -20, y = 0}
        },
        [9] = { -- Trol
            high = {point = "TOPRIGHT", relPoint = "TOPLEFT", x = -20, y = 40},
            veryLow = {point = "BOTTOMRIGHT", relPoint = "TOPLEFT", x = -20, y = -80},
            default = {point = "RIGHT", relPoint = "LEFT", x = -20, y = 20}
        },
        [10] = { -- Elfo de sangre
            high = {point = "TOPRIGHT", relPoint = "TOPLEFT", x = -20, y = 20},
            veryLow = {point = "BOTTOMRIGHT", relPoint = "TOPLEFT", x = -20, y = -120},
            default = {point = "RIGHT", relPoint = "LEFT", x = -20, y = 0}
        }
    }
}

function GetRaceTooltipPosition(raceID, button)
    local screenHeight = GetScreenHeight()
    local buttonTop = button:GetTop()
    local buttonBottom = button:GetBottom()

    local faction = GetFactionForRaceID(raceID)
    local positions = RaceTooltipPositions[faction][raceID]

    if not positions then
        return {point = "CENTER", relPoint = "CENTER", x = 0, y = 0}
    end

    if buttonTop > screenHeight * 0.66 then
        return positions.high
    elseif buttonBottom < screenHeight * 0.44 and positions.low then
        return positions.low
    elseif buttonBottom < screenHeight * 0.33 and positions.veryLow then
        return positions.veryLow
    else
        return positions.default
    end
end

local RACE_DATA = {
    [1]  = { glueString = "HUMAN",     faction = "Alliance" },
    [2]  = { glueString = "DWARF",     faction = "Alliance" },
    [3]  = { glueString = "NIGHT_ELF", faction = "Alliance" },
    [4]  = { glueString = "GNOME",     faction = "Alliance" },
    [5]  = { glueString = "DRAENEI",   faction = "Alliance" },
    [6]  = { glueString = "WORGEN",    faction = "Alliance" },
    [7]  = { glueString = "HIGHELF",   faction = "Alliance" },
    [8]  = { glueString = "SETHRAK",   faction = "Horde" },
    [9]  = { glueString = "ORC",       faction = "Horde" },
    [10] = { glueString = "SCOURGE",   faction = "Horde" },
    [11] = { glueString = "TAUREN",    faction = "Horde" },
    [12] = { glueString = "TROLL",     faction = "Horde" },
    [13] = { glueString = "GOBLIN",    faction = "Horde" },
    [14] = { glueString = "BROKEN",   faction = "Horde" },
    [15] = { glueString = "MAGHAR",    faction = "Horde" },
    [16] = { glueString = "PANDAREN", faction = "Alliance" },
    [17] = { glueString = "VULPERA",  faction = "Horde" },
    [18] = { glueString = "DARKFALLEN", faction = "Alliance" },
    [19] = { glueString = "DARKFALLEN", faction = "Horde" },
}

local EXACT_RACE_DATA = {
    [54] = { glueString="NAGAHORDE", name="Naga", faction="Horde", fileString="NagaHorde" },
    [55] = { glueString="TUSKARR", name="Tuskarr", faction="Alliance", fileString="Tuskarr" },
    [56] = { glueString="VRYKUL", name="Vrykul", faction="Alliance", fileString="Vrykul" },
    [57] = { glueString="VRYKULHORDE", name="Vrykul", faction="Horde", fileString="VrykulHorde" },
    [58] = { glueString="THINHUMAN", name="Human", faction="Alliance", fileString="ThinHuman" },
    [59] = { glueString="THINHUMANHORDE", name="Human", faction="Horde", fileString="ThinHumanHorde" },
    [20] = { glueString="VULPERA", name="Vulpera", faction="Horde", fileString="Vulpera" },
    [50] = { glueString="HARANIR", name="Haranir", faction="Alliance", fileString="Haranir" },
    [51] = { glueString="HARANIRHORDE", name="Haranir", faction="Horde", fileString="HaranirHorde" },
    [48] = { glueString="EARTHEN", name="Earthen", faction="Alliance", fileString="Earthen" },
    [49] = { glueString="EARTHENHORDE", name="Earthen", faction="Horde", fileString="EarthenHorde" },
    [46] = { glueString = "HIGHMOUNTAINTAUREN", name = "Highmountain Tauren", faction = "Horde", fileString = "HighmountainTauren" },
    [47] = { glueString = "MECHAGNOME", name = "Mechagnome", faction = "Alliance", fileString = "Mechagnome" },
    [52] = { glueString = "SKYBORNE", name = "High Order Skyborne", faction = "Alliance", fileString = "Skyborne" },
    [53] = { glueString = "SKYBORNEHORDE", name = "Windshaper Skyborne", faction = "Horde", fileString = "SkyborneHorde" },
    [45] = { glueString = "MAGHAR", name = "Mag'har Orc", faction = "Horde", fileString = "Maghar" },
}

local EXACT_RACE_ID_BY_FILE_STRING = {}
for exactRaceID, exactRaceData in pairs(EXACT_RACE_DATA) do
    if exactRaceData.fileString then
        EXACT_RACE_ID_BY_FILE_STRING[strupper(exactRaceData.fileString)] = exactRaceID
    end
end

local function GetExactRaceIDForFileString(fileString)
    if not fileString then
        return nil
    end
    return EXACT_RACE_ID_BY_FILE_STRING[strupper(fileString)]
end

local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7, 16, 18}
local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17, 19}

local function GetRaceName(raceID)
    local exactRaceData = EXACT_RACE_DATA[raceID]
    if exactRaceData then
        return exactRaceData.name
    end

    local raceData = RACE_DATA[raceID]
    if not raceData then
        return "Human"
    end

    return _G[raceData.glueString] or raceData.glueString
end

local function GetFactionForRaceID(raceID)
    local exactRaceData = EXACT_RACE_DATA[raceID]
    if exactRaceData then
        return exactRaceData.faction
    end

    local _, faction = GetFactionForRace(raceID)
    if faction then
        return faction
    end
    local raceData = RACE_DATA[raceID]
    return raceData and raceData.faction or "Alliance"
end

local function GetRaceNamesByFaction(faction)
    local names = {}
    local raceList = (faction == "Alliance") and ALLIANCE_RACES or HORDE_RACES

    for _, raceID in ipairs(raceList) do
        table.insert(names, GetRaceName(raceID))
    end

    return names
end

local AllianceRaces = GetRaceNamesByFaction("Alliance")
local HordeRaces = GetRaceNamesByFaction("Horde")

local function GetCurrentRaceName()
    local raceID = GetSelectedRace()
    return GetRaceName(raceID)
end

local function GetRacesByFaction(allowedRaces)
    local allianceList = {}
    local hordeList = {}

    for _, race in ipairs(allowedRaces) do
        local isAlliance = false
        for _, allianceRace in ipairs(AllianceRaces) do
            if race == allianceRace then
                table.insert(allianceList, race)
                isAlliance = true
                break
            end
        end

        if not isAlliance then
            for _, hordeRace in ipairs(HordeRaces) do
                if race == hordeRace then
                    table.insert(hordeList, race)
                    break
                end
            end
        end
    end

    return allianceList, hordeList
end

local RACE_NAME_CACHE = {}

local function GetFactionForRaceName(raceName)
    if not raceName then return "Horde" end

    if RACE_NAME_CACHE[raceName] then
        return RACE_NAME_CACHE[raceName]
    end

    for _, raceData in pairs(EXACT_RACE_DATA) do
        if raceData.name == raceName then
            RACE_NAME_CACHE[raceName] = raceData.faction
            return raceData.faction
        end
    end

    local currentLocale = GetLocale()
    local faction = nil

    for _, raceData in pairs(RACE_DATA) do
        local baseKey = raceData.glueString

        for _, genderKey in ipairs({"_MALE", "_FEMALE"}) do
            local fullKey = baseKey .. genderKey
            local localizedName = _G[fullKey]

            if localizedName and localizedName == raceName then
                faction = raceData.faction
                break
            end
        end

        if faction then
            break
        end
    end

    if not faction then
        faction = "Horde"
    end

    RACE_NAME_CACHE[raceName] = faction
    return faction
end

_G.RACE_1 = "Humano"
_G.RACE_2 = "Enano"
_G.RACE_3 = "Elfo de la noche"
_G.RACE_4 = "Gnomo"
_G.RACE_5 = "Draenei"
_G.RACE_6 = "Worgen"
_G.RACE_7 = "High Elf"
_G.RACE_8 = "Sethrak"
_G.RACE_9 = "Orc"
_G.RACE_10 = "Undead"
_G.RACE_11 = "Tauren"
_G.RACE_12 = "Troll"
_G.RACE_13 = "Goblin"
_G.RACE_14 = "Broken"
_G.RACE_15 = "Mag'har Orc"
_G.RACE_18 = "Darkfallen"
_G.RACE_19 = "Darkfallen"
_G.WORGEN = "Worgen"
_G.HIGHELF = "High Elf"
_G.GOBLIN = "Goblin"
_G.MAGHAR = "Mag'har Orc"
_G.SETHRAK = "Sethrak"
_G.WORGEN_MALE = "Worgen"
_G.WORGEN_FEMALE = "Worgen"
_G.HIGHELF_MALE = "High Elf"
_G.HIGHELF_FEMALE = "High Elf"
_G.GOBLIN_MALE = "Goblin"
_G.GOBLIN_FEMALE = "Goblin"
_G.MAGHAR_MALE = "Mag'har Orc"
_G.MAGHAR_FEMALE = "Mag'har Orc"
_G.SETHRAK_MALE = "Sethrak"
_G.SETHRAK_FEMALE = "Sethrak"
_G.BROKEN = "Broken"
_G.BROKEN_MALE = "Broken"
_G.BROKEN_FEMALE = "Broken"
_G.DARKFALLEN = "Darkfallen"
_G.DARKFALLEN_MALE = "Darkfallen"
_G.DARKFALLEN_FEMALE = "Darkfallen"

local function GetGlueText(key, fallback)
    return _G[key] or fallback
end

local raceLocalization = {
    [1] = {token = "HUMAN", name = "Human", spells = {"Every Man for Himself", "Sword Specialization", "Mace Specialization", "The Human Spirit", "Perception", "Diplomacy"}},
    [2] = {token = "DWARF", name = "Dwarf", spells = {"Mace Specialization", "Stoneform", "Gun Specialization", "Frost Resistance", "Find Treasure"}},
    [3] = {token = "NIGHTELF", name = "Night Elf", spells = {"Shadowmeld", "Elusiveness", "Nature Resistance", "Quickness", "Wisp Spirit"}},
    [4] = {token = "GNOME", name = "Gnome", spells = {"Escape Artist", "Arcane Resistance", "Expansive Mind", "Engineering Specialization"}},
    [5] = {token = "DRAENEI", name = "Draenei", spells = {"Gift of the Naaru", "Gemcutting", "Heroic Presence", "Shadow Resistance"}},
    [6] = {token = "WORGEN", name = "Worgen", spells = {"Aberration", "Two Forms", "Running Wild"}},
    [7] = {token = "HIGHELF", name = "High Elf", spells = {"Arcane Affinity", "Arcane Acuity", "Bow Specialization", "Enchanting"}},
    [8] = {token = "SETHRAK", name = "Sethrak", spells = {"Sandswept", "Desert Mastery"}},
    [9] = {token = "ORC", name = "Orc", spells = {"Blood Fury", "Command", "Hardiness", "Axe Specialization"}},
    [10] = {token = "SCOURGE", name = "Undead", spells = {"Cannibalize", "Will of the Forsaken", "Shadow Resistance", "Underwater Breathing"}},
    [11] = {token = "TAUREN", name = "Tauren", spells = {"War Stomp", "Endurance", "Nature Resistance", "Cultivation"}},
    [12] = {token = "TROLL", name = "Troll", spells = {"Berserking", "Regeneration", "Beast Slaying", "Throwing Weapon Specialization", "Bow Specialization", "Da Voodoo Shuffle"}},
    [13] = {token = "GOBLIN", name = "Goblin", spells = {"Best Deals Anywhere", "Alchemy", "Gobber", "Rocket Barrage", "Rocket Jump", "Time is Money"}},
    [14] = {token = "BROKEN", name = "Broken", spells = {"Salvager", "Krokul Cunning", "Fel-Scarred", "Echo of the Naaru"}},
    [15] = {token = "MAGHAR", name = "Mag'har Orc", spells = {"Ancestral Call", "Savage Blood", "Sympathetic Vigor", "Unwavering Will"}},
    [16] = {token = "PANDAREN", name = "Pandaren", spells = {}},
    [17] = {token = "VULPERA", name = "Vulpera", spells = {}},
    [18] = {token = "DARKFALLEN", name = "Darkfallen", spells = {"Crimson Thirst", "Shadow Resistance", "Vampiric Sustenance", "Children of the Night"}},
}

for raceID, data in pairs(raceLocalization) do
    local info = Races_Informations[raceID]
    if info then
        info.Name = data.name
        info.Description = GetGlueText("RACE_INFO_" .. data.token, info.Description)
        for spellIndex, spellName in ipairs(data.spells) do
            local spell = info["Spell_" .. spellIndex]
            if spell then
                spell.name = spellName
                spell.description = GetGlueText("ABILITY_INFO_" .. data.token .. spellIndex, spell.description)
            end
        end
    end
    _G["RACE_" .. raceID] = data.name
end

bloodElfInfo.Name = "Blood Elf"
bloodElfInfo.Description = GetGlueText(
    "RACE_INFO_BLOODELF",
    "Long ago the exiled high elves founded Quel'Thalas, where they created a magical fount called the Sunwell. Though they were strengthened by its powers, they also grew increasingly dependent on them.|n|n" ..
    "Ages later the undead Scourge destroyed the Sunwell and most of the high elf population. Now called blood elves, these scattered refugees are rebuilding Quel'Thalas as they search for a new magic source to satisfy their painful addiction."
)

local classLocalization = {
    [1] = {Name = "Warrior", Description = "Masters of armed combat who use strength and armor to protect allies and defeat enemies.", Roles = "Melee Damage, Tank."},
    [2] = {Name = "Paladin", Description = "Holy warriors who combine martial skill with divine magic to protect and heal their allies.", Roles = "Melee Damage, Tank, Healer."},
    [3] = {Name = "Hunter", Description = "Ranged fighters who track enemies, set traps, and fight alongside loyal animal companions.", Roles = "Ranged Damage."},
    [4] = {Name = "Rogue", Description = "Masters of stealth and deception who strike from the shadows with speed and precision.", Roles = "Melee Damage."},
    [5] = {Name = "Priest", Description = "Wielders of divine and shadow magic who restore health, protect allies, and punish enemies.", Roles = "Ranged Damage, Healer."},
    [6] = {Name = "Death Knight", Description = "Undead warriors who combine martial skill with necromantic and shadow magic.", Roles = "Melee Damage, Tank."},
    [7] = {Name = "Shaman", Description = "Elemental spellcasters who call on spirits and totems to heal allies or destroy enemies.", Roles = "Melee Damage, Ranged Damage, Healer."},
    [8] = {Name = "Mage", Description = "Fragile but powerful spellcasters who command fire, frost, and arcane magic.", Roles = "Ranged Damage."},
    [9] = {Name = "Warlock", Description = "Dark spellcasters who drain life, corrupt enemies, and summon demonic servants.", Roles = "Ranged Damage."},
    [10] = {Name = "Druid", Description = "Versatile guardians of nature who shift forms to heal, tank, or deal damage.", Roles = "Melee Damage, Ranged Damage, Tank, Healer."},
}

for classID, data in pairs(classLocalization) do
    Class_Informations[classID] = data
end

_G.Races_Informations = Races_Informations
_G.RaceInfoByFileString = raceInfoByFileString
_G.Class_Informations = Class_Informations
_G.ClassRaces = ClassRaces or {}
_G.GetRaceTooltipPosition = GetRaceTooltipPosition

_G.GetRaceName = GetRaceName
_G.GetFactionForRaceID = GetFactionForRaceID
_G.GetRaceNamesByFaction = GetRaceNamesByFaction
_G.GetCurrentRaceName = GetCurrentRaceName
_G.GetRacesByFaction = GetRacesByFaction

_G.ALLIANCE_RACES = ALLIANCE_RACES
_G.HORDE_RACES = HORDE_RACES
_G.RACE_DATA = RACE_DATA
_G.EXACT_RACE_DATA = EXACT_RACE_DATA
_G.GetExactRaceIDForFileString = GetExactRaceIDForFileString
_G.AllianceRaces = AllianceRaces
_G.HordeRaces = HordeRaces

_G.GetFactionForRaceName = GetFactionForRaceName

-- Retroported race presentation: preserve the installed racial abilities and use distinct lore/name tables.
local skybornDescriptions = {
    SKYBORNE = "Azure-skinned elves distinguished by their feathered hair and keen magical senses. "
        .. "The High Order stand with the Alliance.",
    SKYBORNEHORDE = "Azure-skinned elves distinguished by their feathered hair and keen magical senses. "
        .. "The Windshapers stand with the Horde.",
};
for token,description in pairs(skybornDescriptions) do
    local source = RaceInfoByFileString[token];
    local info = {};
    for key,value in pairs(source or {}) do info[key] = value; end
    info.Name = token == "SKYBORNE" and "High Order Skyborn" or "Windshaper Skyborn";
    info.Description = description;
    RaceInfoByFileString[token] = info;
    _G["RACE_INFO_"..token] = description;
    _G["RACE_INFO_"..token.."_FEMALE"] = description;
end

RaceInfoByFileString.MECHAGNOME = {Name="Mechagnome", Description="The clever mechagnomes balance flesh with technology, making them innovative allies of the Alliance.", RacialTraits={}};

local highmountainInfo = {};
for key,value in pairs(RaceInfoByFileString.TAUREN or {}) do highmountainInfo[key]=value; end
highmountainInfo.Name="Highmountain Tauren";
highmountainInfo.Description="Descendants of Huln Highmountain, these tauren honor the spirits of earth, river, and sky. United beneath their ancestral antlers, the tribes of Highmountain stand with their kin in the Horde.";
RaceInfoByFileString.HIGHMOUNTAINTAUREN=highmountainInfo;

local earthenInfo = {};
for key,value in pairs(RaceInfoByFileString.DWARF or {}) do earthenInfo[key]=value; end
earthenInfo.Name="Earthen"; earthenInfo.Description="Forged by the titans from living stone, the earthen have broken free of their ancient edicts. They venture beyond Khaz Algar with curiosity and resolve, choosing their own paths in Azeroth.";
RaceInfoByFileString.EARTHEN=earthenInfo;

local earthenInfo = {};
for key,value in pairs(RaceInfoByFileString.ORC or {}) do earthenInfo[key]=value; end
earthenInfo.Name="Earthen"; earthenInfo.Description="Forged by the titans from living stone, the earthen have broken free of their ancient edicts. They venture beyond Khaz Algar with curiosity and resolve, choosing their own paths in Azeroth.";
RaceInfoByFileString.EARTHENHORDE=earthenInfo;

local haranirInfo = {};
for key,value in pairs(RaceInfoByFileString.NIGHTELF or {}) do haranirInfo[key]=value; end
haranirInfo.Name="Haranir"; haranirInfo.Description="Ferocious, watchful guardians, the haranir keep an ever-present vigil over the wild domains of their long-absent Goddess, in hopes that she might one day return.";
RaceInfoByFileString.HARANIR=haranirInfo;

local haranirInfo = {};
for key,value in pairs(RaceInfoByFileString.TROLL or {}) do haranirInfo[key]=value; end
haranirInfo.Name="Haranir"; haranirInfo.Description="Ferocious, watchful guardians, the haranir keep an ever-present vigil over the wild domains of their long-absent Goddess, in hopes that she might one day return.";
RaceInfoByFileString.HARANIRHORDE=haranirInfo;

do local info = {};
for key,value in pairs(RaceInfoByFileString.ORC or {}) do info[key]=value; end
info.Name="Naga";
RaceInfoByFileString.NAGAHORDE=info; end

do local info = {};
for key,value in pairs(RaceInfoByFileString.DWARF or {}) do info[key]=value; end
info.Name="Tuskarr";
RaceInfoByFileString.TUSKARR=info; end

do local info = {};
for key,value in pairs(RaceInfoByFileString.HUMAN or {}) do info[key]=value; end
info.Name="Vrykul";
RaceInfoByFileString.VRYKUL=info; end

do local info = {};
for key,value in pairs(RaceInfoByFileString.ORC or {}) do info[key]=value; end
info.Name="Vrykul";
RaceInfoByFileString.VRYKULHORDE=info; end

do local info = {};
for key,value in pairs(RaceInfoByFileString.HUMAN or {}) do info[key]=value; end
info.Name="Human";
RaceInfoByFileString.THINHUMAN=info; end

do local info = {};
for key,value in pairs(RaceInfoByFileString.ORC or {}) do info[key]=value; end
info.Name="Human";
RaceInfoByFileString.THINHUMANHORDE=info; end
