package com.create_skybound.registry;

import com.create_skybound.CreateSkybound;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUND_EVENTS =
            DeferredRegister.create(Registries.SOUND_EVENT, CreateSkybound.MODID);

    public static final DeferredHolder<SoundEvent, SoundEvent> WINCH_WIND = registerSound("winch_wind");
    public static final DeferredHolder<SoundEvent, SoundEvent> CLAMP_LOCK = registerSound("clamp_lock");
    public static final DeferredHolder<SoundEvent, SoundEvent> CLAMP_UNLOCK = registerSound("clamp_unlock");
    public static final DeferredHolder<SoundEvent, SoundEvent> GANGWAY_EXTEND = registerSound("gangway_extend");
    public static final DeferredHolder<SoundEvent, SoundEvent> RADAR_PING = registerSound("radar_ping");
    public static final DeferredHolder<SoundEvent, SoundEvent> RADAR_ALERT = registerSound("radar_alert");
    public static final DeferredHolder<SoundEvent, SoundEvent> BEACON_PULSE = registerSound("beacon_pulse");
    public static final DeferredHolder<SoundEvent, SoundEvent> BALLAST_VENT = registerSound("ballast_vent");
    public static final DeferredHolder<SoundEvent, SoundEvent> FLARE_FIRE = registerSound("flare_fire");
    public static final DeferredHolder<SoundEvent, SoundEvent> BUMPER_IMPACT = registerSound("bumper_impact");

    private static DeferredHolder<SoundEvent, SoundEvent> registerSound(String name) {
        ResourceLocation id = ResourceLocation.fromNamespaceAndPath(CreateSkybound.MODID, name);
        return SOUND_EVENTS.register(name, () -> SoundEvent.createVariableRangeEvent(id));
    }
}
