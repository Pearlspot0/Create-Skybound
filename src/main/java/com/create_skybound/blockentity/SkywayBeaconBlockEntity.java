package com.create_skybound.blockentity;

import com.create_skybound.block.SkywayBeaconBlock;
import com.create_skybound.registry.ModBlockEntities;
import com.create_skybound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import org.joml.Vector3f;

import java.util.Collections;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public class SkywayBeaconBlockEntity extends BlockEntity {
    public static final Set<SkywayBeaconBlockEntity> ACTIVE_BEACONS = Collections.newSetFromMap(new ConcurrentHashMap<>());

    private int tickCount = 0;
    private String customName = "";

    public SkywayBeaconBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.SKYWAY_BEACON.get(), pos, state);
    }

    @Override
    public void onLoad() {
        super.onLoad();
        ACTIVE_BEACONS.add(this);
    }

    @Override
    public void setRemoved() {
        ACTIVE_BEACONS.remove(this);
        super.setRemoved();
    }

    public static void tick(Level level, BlockPos pos, BlockState state, SkywayBeaconBlockEntity beacon) {
        beacon.tickCount++;

        if (level.isClientSide) {
            DyeColor color = state.getValue(SkywayBeaconBlock.COLOR);
            int rgb = color.getTextureDiffuseColor();
            float r = ((rgb >> 16) & 0xFF) / 255.0f;
            float g = ((rgb >> 8) & 0xFF) / 255.0f;
            float b = (rgb & 0xFF) / 255.0f;

            // Spawn upward vertical light beam particles
            if (beacon.tickCount % 2 == 0) {
                DustParticleOptions dust = new DustParticleOptions(new Vector3f(r, g, b), 1.5f);
                for (int y = 1; y <= 16; y += 3) {
                    level.addParticle(dust, pos.getX() + 0.5, pos.getY() + y, pos.getZ() + 0.5, 0, 0.2, 0);
                }
            }
        } else {
            if (beacon.tickCount % 100 == 0) {
                level.playSound(null, pos, ModSounds.BEACON_PULSE.get(), SoundSource.BLOCKS, 0.5f, 1.0f);
            }
        }
    }

    @Nullable
    public static SkywayBeaconBlockEntity findNearest(Level level, Vec3 fromPos) {
        SkywayBeaconBlockEntity nearest = null;
        double minDistSq = Double.MAX_VALUE;
        ResourceKey<Level> dim = level.dimension();

        for (SkywayBeaconBlockEntity beacon : ACTIVE_BEACONS) {
            if (beacon.isRemoved() || beacon.getLevel() == null) continue;
            if (!beacon.getLevel().dimension().equals(dim)) continue;

            double distSq = fromPos.distanceToSqr(Vec3.atCenterOf(beacon.getBlockPos()));
            if (distSq < minDistSq) {
                minDistSq = distSq;
                nearest = beacon;
            }
        }
        return nearest;
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.putString("CustomName", customName);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        customName = tag.getString("CustomName");
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        CompoundTag tag = super.getUpdateTag(registries);
        saveAdditional(tag, registries);
        return tag;
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }
}
