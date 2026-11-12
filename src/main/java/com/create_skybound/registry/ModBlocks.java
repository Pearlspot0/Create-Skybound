package com.create_skybound.registry;

import com.create_skybound.CreateSkybound;
import com.create_skybound.block.*;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(CreateSkybound.MODID);

    public static final DeferredBlock<MooringWinchBlock> MOORING_WINCH = BLOCKS.register("mooring_winch",
            () -> new MooringWinchBlock(BlockBehaviour.Properties.of()
                    .strength(3.5F, 6.0F)
                    .sound(SoundType.COPPER)
                    .requiresCorrectToolForDrops()));

    public static final DeferredBlock<MooringCleatBlock> MOORING_CLEAT = BLOCKS.register("mooring_cleat",
            () -> new MooringCleatBlock(BlockBehaviour.Properties.of()
                    .strength(2.0F, 4.0F)
                    .sound(SoundType.METAL)
                    .noOcclusion()));

    public static final DeferredBlock<DockingClampBlock> DOCKING_CLAMP = BLOCKS.register("docking_clamp",
            () -> new DockingClampBlock(BlockBehaviour.Properties.of()
                    .strength(4.0F, 8.0F)
                    .sound(SoundType.NETHERITE_BLOCK)
                    .requiresCorrectToolForDrops()));

    public static final DeferredBlock<DockingGangwayBlock> DOCKING_GANGWAY = BLOCKS.register("docking_gangway",
            () -> new DockingGangwayBlock(BlockBehaviour.Properties.of()
                    .strength(3.0F, 6.0F)
                    .sound(SoundType.COPPER)
                    .noOcclusion()));

    public static final DeferredBlock<DockingGangwaySegmentBlock> DOCKING_GANGWAY_SEGMENT = BLOCKS.register("docking_gangway_segment",
            () -> new DockingGangwaySegmentBlock(BlockBehaviour.Properties.of()
                    .strength(1.5F, 3.0F)
                    .sound(SoundType.COPPER)
                    .noOcclusion()
                    .noLootTable()));

    public static final DeferredBlock<AltimeterGaugeBlock> ALTIMETER_GAUGE = BLOCKS.register("altimeter_gauge",
            () -> new AltimeterGaugeBlock(BlockBehaviour.Properties.of()
                    .strength(1.0F, 2.0F)
                    .sound(SoundType.METAL)
                    .noOcclusion()));

    public static final DeferredBlock<VariometerGaugeBlock> VARIOMETER_GAUGE = BLOCKS.register("variometer_gauge",
            () -> new VariometerGaugeBlock(BlockBehaviour.Properties.of()
                    .strength(1.0F, 2.0F)
                    .sound(SoundType.METAL)
                    .noOcclusion()));

    public static final DeferredBlock<AirspeedGaugeBlock> AIRSPEED_GAUGE = BLOCKS.register("airspeed_gauge",
            () -> new AirspeedGaugeBlock(BlockBehaviour.Properties.of()
                    .strength(1.0F, 2.0F)
                    .sound(SoundType.METAL)
                    .noOcclusion()));

    public static final DeferredBlock<AirspaceRadarBlock> AIRSPACE_RADAR = BLOCKS.register("airspace_radar",
            () -> new AirspaceRadarBlock(BlockBehaviour.Properties.of()
                    .strength(3.0F, 6.0F)
                    .sound(SoundType.COPPER)
                    .lightLevel(state -> state.getValue(AirspaceRadarBlock.LIT) ? 10 : 0)));

    public static final DeferredBlock<SkywayBeaconBlock> SKYWAY_BEACON = BLOCKS.register("skyway_beacon",
            () -> new SkywayBeaconBlock(BlockBehaviour.Properties.of()
                    .strength(3.0F, 6.0F)
                    .sound(SoundType.GLASS)
                    .lightLevel(state -> 15)
                    .noOcclusion()));

    public static final DeferredBlock<AirshipBumperBlock> AIRSHIP_BUMPER = BLOCKS.register("airship_bumper",
            () -> new AirshipBumperBlock(BlockBehaviour.Properties.of()
                    .strength(1.5F, 3.0F)
                    .sound(SoundType.WOOL)));

    public static final DeferredBlock<BallastVentBlock> BALLAST_VENT = BLOCKS.register("ballast_vent",
            () -> new BallastVentBlock(BlockBehaviour.Properties.of()
                    .strength(3.0F, 6.0F)
                    .sound(SoundType.METAL)));

    public static final DeferredBlock<AeroBrassCasingBlock> AERO_BRASS_CASING = BLOCKS.register("aero_brass_casing",
            () -> new AeroBrassCasingBlock(BlockBehaviour.Properties.of()
                    .strength(3.0F, 8.0F)
                    .sound(SoundType.COPPER)
                    .requiresCorrectToolForDrops()));

    public static final DeferredBlock<AeroBrassStrutBlock> AERO_BRASS_STRUT = BLOCKS.register("aero_brass_strut",
            () -> new AeroBrassStrutBlock(BlockBehaviour.Properties.of()
                    .strength(2.5F, 6.0F)
                    .sound(SoundType.COPPER)
                    .noOcclusion()));
}
