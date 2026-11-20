"""`armor stand thaw`: an armor stand's `TicksFrozen` thaws and builds as `LivingEntity.aiStep` runs it."""

GROUP = 'armor stand thaw'

# (summon NBT, block under the stand's feet and body)
STANDS = [
    ('TicksFrozen:60', None),  # in the open: two a tick
    ('TicksFrozen:60,NoGravity:1b', None),  # no physics, still thaws
    ('TicksFrozen:60,Marker:1b', None),
    ('TicksFrozen:1', None),  # thaws to 0, and the key goes
    ('', 'powder_snow'),  # builds one a tick
    ('TicksFrozen:139', 'powder_snow'),  # up to getTicksRequiredToFreeze (140)
    ('TicksFrozen:60,equipment:{feet:{id:"leather_boots",count:1}}', 'powder_snow'),  # freeze_immune_wearables
    ('TicksFrozen:60,NoGravity:1b', 'powder_snow'),  # no block effects reach it: thaws
    ('TicksFrozen:60,equipment:{head:{id:"leather_helmet",count:1}}', 'powder_snow'),
    ('TicksFrozen:60,equipment:{chest:{id:"iron_chestplate",count:1}}', 'powder_snow'),  # iron: freezes
]


def cases(cmd, setup):
    """`LivingEntity.aiStep`'s freezing step after `applyEffectsFromBlocks`: powder snow's
    `InsideBlockEffectType.FREEZE` adds one while `canFreeze`, otherwise `TicksFrozen` drops by two
    (never below 0, and `saveWithoutId` writes it only while positive). Each stand is read after 1,
    2 and 20 ticks."""
    x0, y0, z0 = 7520, 250, 7520
    ops = [cmd(f'/forceload add {x0} {z0}', False), {'op': 'wait_chunks', 'chunks': [[x0 >> 4, z0 >> 4]]},
           cmd(f'/fill {x0} {y0 - 1} {z0} {x0 + 15} {y0 - 1} {z0 + 15} stone', False)]
    for n, (nbt, block) in enumerate(STANDS):
        x, z = x0 + 1 + n % 5 * 3, z0 + 2 + n // 5 * 4
        if block:
            ops.append(cmd(f'/fill {x} {y0} {z} {x} {y0 + 1} {z} {block}', False))
        sep = ',' if nbt else ''
        ops.append(cmd(f'/summon armor_stand {x}.5 {y0} {z}.5 {{UUID:[I;43,0,0,{n}]{sep}{nbt}}}', False))
    for step in (1, 1, 18):
        ops.append({'op': 'tick', 'n': step})
        for n in range(len(STANDS)):
            ops.append(cmd(f'/data get entity 0000002b-0000-0000-0000-{n:012x} TicksFrozen'))
    return ops + setup(f'/kill @e[type=!player,x={x0},y={y0 - 8},z={z0},dx=16,dy=16,dz=16]',
                       f'/fill {x0} {y0 - 2} {z0} {x0 + 15} {y0 + 4} {z0 + 15} air',
                       f'/forceload remove {x0} {z0}')
