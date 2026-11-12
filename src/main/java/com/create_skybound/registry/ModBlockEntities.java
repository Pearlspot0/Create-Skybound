package com.create_skybound.registry;

import com.create_skybound.CreateSkybound;
import com.create_skybound.blockentity.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, CreateSkybound.MODID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<MooringCleatBlockEntity>> MOORING_CLEAT =
            BLOCK_ENTITIES.register("mooring_cleat", () ->
                    BlockEntityType.Builder.of(MooringCleatBlockEntity::new, ModBlocks.MOORING_CLEAT.get()).build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<MooringWinchBlockEntity>> MOORING_WINCH =
            BLOCK_ENTITIES.register("mooring_winch", () ->
                    BlockEntityType.Builder.of(MooringWinchBlockEntity::new, ModBlocks.MOORING_WINCH.get()).build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<DockingClampBlockEntity>> DOCKING_CLAMP =
            BLOCK_ENTITIES.register("docking_clamp", () ->
                    BlockEntityType.Builder.of(DockingClampBlockEntity::new, ModBlocks.DOCKING_CLAMP.get()).build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<AirspaceRadarBlockEntity>> AIRSPACE_RADAR =
            BLOCK_ENTITIES.register("airspace_radar", () ->
                    BlockEntityType.Builder.of(AirspaceRadarBlockEntity::new, ModBlocks.AIRSPACE_RADAR.get()).build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<SkywayBeaconBlockEntity>> SKYWAY_BEACON =
            BLOCK_ENTITIES.register("skyway_beacon", () ->
                    BlockEntityType.Builder.of(SkywayBeaconBlockEntity::new, ModBlocks.SKYWAY_BEACON.get()).build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<BallastVentBlockEntity>> BALLAST_VENT =
            BLOCK_ENTITIES.register("ballast_vent", () ->
                    BlockEntityType.Builder.of(BallastVentBlockEntity::new, ModBlocks.BALLAST_VENT.get()).build(null));
}
