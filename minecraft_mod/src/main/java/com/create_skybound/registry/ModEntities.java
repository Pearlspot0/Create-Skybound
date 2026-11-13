package com.create_skybound.registry;

import com.create_skybound.CreateSkybound;
import com.create_skybound.entity.SignalFlareEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(Registries.ENTITY_TYPE, CreateSkybound.MODID);

    public static final DeferredHolder<EntityType<?>, EntityType<SignalFlareEntity>> SIGNAL_FLARE =
            ENTITY_TYPES.register("signal_flare", () ->
                    EntityType.Builder.<SignalFlareEntity>of(SignalFlareEntity::new, MobCategory.MISC)
                            .sized(0.25F, 0.25F)
                            .clientTrackingRange(10)
                            .updateInterval(2)
                            .build("signal_flare"));
}
