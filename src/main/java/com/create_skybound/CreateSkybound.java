package com.create_skybound;

import com.create_skybound.registry.*;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

@Mod(CreateSkybound.MODID)
public class CreateSkybound {
    public static final String MODID = "create_skybound";
    public static final Logger LOGGER = LogUtils.getLogger();

    public CreateSkybound(IEventBus modEventBus) {
        LOGGER.info("Initializing Create: Skybound for All of Create modpack!");

        ModSounds.SOUND_EVENTS.register(modEventBus);
        ModBlocks.BLOCKS.register(modEventBus);
        ModItems.ITEMS.register(modEventBus);
        ModBlockEntities.BLOCK_ENTITIES.register(modEventBus);
        ModEntities.ENTITY_TYPES.register(modEventBus);
        ModCreativeTabs.CREATIVE_MODE_TABS.register(modEventBus);
    }
}
