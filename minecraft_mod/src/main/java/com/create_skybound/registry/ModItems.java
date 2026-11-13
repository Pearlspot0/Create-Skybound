package com.create_skybound.registry;

import com.create_skybound.CreateSkybound;
import com.create_skybound.item.*;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(CreateSkybound.MODID);

    // Block Items
    public static final DeferredItem<BlockItem> MOORING_WINCH = ITEMS.registerSimpleBlockItem(ModBlocks.MOORING_WINCH);
    public static final DeferredItem<BlockItem> MOORING_CLEAT = ITEMS.registerSimpleBlockItem(ModBlocks.MOORING_CLEAT);
    public static final DeferredItem<BlockItem> DOCKING_CLAMP = ITEMS.registerSimpleBlockItem(ModBlocks.DOCKING_CLAMP);
    public static final DeferredItem<BlockItem> DOCKING_GANGWAY = ITEMS.registerSimpleBlockItem(ModBlocks.DOCKING_GANGWAY);
    public static final DeferredItem<BlockItem> ALTIMETER_GAUGE = ITEMS.registerSimpleBlockItem(ModBlocks.ALTIMETER_GAUGE);
    public static final DeferredItem<BlockItem> VARIOMETER_GAUGE = ITEMS.registerSimpleBlockItem(ModBlocks.VARIOMETER_GAUGE);
    public static final DeferredItem<BlockItem> AIRSPEED_GAUGE = ITEMS.registerSimpleBlockItem(ModBlocks.AIRSPEED_GAUGE);
    public static final DeferredItem<BlockItem> AIRSPACE_RADAR = ITEMS.registerSimpleBlockItem(ModBlocks.AIRSPACE_RADAR);
    public static final DeferredItem<BlockItem> SKYWAY_BEACON = ITEMS.registerSimpleBlockItem(ModBlocks.SKYWAY_BEACON);
    public static final DeferredItem<BlockItem> AIRSHIP_BUMPER = ITEMS.registerSimpleBlockItem(ModBlocks.AIRSHIP_BUMPER);
    public static final DeferredItem<BlockItem> BALLAST_VENT = ITEMS.registerSimpleBlockItem(ModBlocks.BALLAST_VENT);
    public static final DeferredItem<BlockItem> AERO_BRASS_CASING = ITEMS.registerSimpleBlockItem(ModBlocks.AERO_BRASS_CASING);
    public static final DeferredItem<BlockItem> AERO_BRASS_STRUT = ITEMS.registerSimpleBlockItem(ModBlocks.AERO_BRASS_STRUT);

    // Specialized Pilot & Mooring Equipment
    public static final DeferredItem<MooringCableItem> MOORING_CABLE = ITEMS.register("mooring_cable",
            () -> new MooringCableItem(new Item.Properties().stacksTo(16)));

    public static final DeferredItem<FlightSextantItem> FLIGHT_SEXTANT = ITEMS.register("flight_sextant",
            () -> new FlightSextantItem(new Item.Properties().stacksTo(1)));

    public static final DeferredItem<FlareGunItem> FLARE_GUN = ITEMS.register("flare_gun",
            () -> new FlareGunItem(new Item.Properties().durability(128)));

    public static final DeferredItem<SignalFlareItem> SIGNAL_FLARE = ITEMS.register("signal_flare",
            () -> new SignalFlareItem(new Item.Properties().stacksTo(16), 0xFF3322));

    public static final DeferredItem<AeronautVisorItem> AERONAUT_VISOR = ITEMS.register("aeronaut_visor",
            () -> new AeronautVisorItem(new Item.Properties().stacksTo(1)));

    public static final DeferredItem<TransponderKeyItem> TRANSPONDER_KEY = ITEMS.register("transponder_key",
            () -> new TransponderKeyItem(new Item.Properties().stacksTo(1)));

    public static final DeferredItem<Item> AERO_BRASS_INGOT = ITEMS.register("aero_brass_ingot",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> AERO_BRASS_SHEET = ITEMS.register("aero_brass_sheet",
            () -> new Item(new Item.Properties()));
}
