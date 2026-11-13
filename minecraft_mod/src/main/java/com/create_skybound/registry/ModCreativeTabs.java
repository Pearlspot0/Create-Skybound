package com.create_skybound.registry;

import com.create_skybound.CreateSkybound;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, CreateSkybound.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> SKYBOUND_TAB =
            CREATIVE_MODE_TABS.register("create_skybound_tab", () ->
                    CreativeModeTab.builder()
                            .title(Component.translatable("itemGroup.create_skybound"))
                            .icon(() -> new ItemStack(ModBlocks.MOORING_WINCH.get()))
                            .displayItems((parameters, output) -> {
                                output.accept(ModBlocks.MOORING_WINCH.get());
                                output.accept(ModBlocks.MOORING_CLEAT.get());
                                output.accept(ModBlocks.DOCKING_CLAMP.get());
                                output.accept(ModBlocks.DOCKING_GANGWAY.get());
                                output.accept(ModBlocks.ALTIMETER_GAUGE.get());
                                output.accept(ModBlocks.VARIOMETER_GAUGE.get());
                                output.accept(ModBlocks.AIRSPEED_GAUGE.get());
                                output.accept(ModBlocks.AIRSPACE_RADAR.get());
                                output.accept(ModBlocks.SKYWAY_BEACON.get());
                                output.accept(ModBlocks.AIRSHIP_BUMPER.get());
                                output.accept(ModBlocks.BALLAST_VENT.get());
                                output.accept(ModBlocks.AERO_BRASS_CASING.get());
                                output.accept(ModBlocks.AERO_BRASS_STRUT.get());

                                output.accept(ModItems.MOORING_CABLE.get());
                                output.accept(ModItems.FLIGHT_SEXTANT.get());
                                output.accept(ModItems.FLARE_GUN.get());
                                output.accept(ModItems.SIGNAL_FLARE.get());
                                output.accept(ModItems.AERONAUT_VISOR.get());
                                output.accept(ModItems.TRANSPONDER_KEY.get());
                                output.accept(ModItems.AERO_BRASS_INGOT.get());
                                output.accept(ModItems.AERO_BRASS_SHEET.get());
                            })
                            .build());
}
