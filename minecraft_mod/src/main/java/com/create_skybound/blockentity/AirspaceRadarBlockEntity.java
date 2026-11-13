package com.create_skybound.blockentity;

import com.create_skybound.block.AirspaceRadarBlock;
import com.create_skybound.registry.ModBlockEntities;
import com.create_skybound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.monster.Phantom;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class AirspaceRadarBlockEntity extends BlockEntity {
    private int contactCount = 0;
    private double nearestDistance = 0.0;
    private String nearestInfo = "None";
    private int tickCount = 0;

    public AirspaceRadarBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.AIRSPACE_RADAR.get(), pos, state);
    }

    public int getComparatorSignal() {
        if (contactCount == 0) return 0;
        return Math.min(15, contactCount * 3);
    }

    public void sendTacticalReport(Player player) {
        if (contactCount == 0) {
            player.displayClientMessage(Component.translatable("message.create_skybound.radar_all_clear"), false);
        } else {
            player.displayClientMessage(Component.translatable("message.create_skybound.radar_contacts",
                    contactCount, String.format("%.1f", nearestDistance), nearestInfo), false);
        }
    }

    public static void tick(Level level, BlockPos pos, BlockState state, AirspaceRadarBlockEntity radar) {
        radar.tickCount++;
        if (radar.tickCount % 20 != 0) return;

        if (level.isClientSide) return;

        double radius = 64.0;
        AABB scanBox = new AABB(pos).inflate(radius);
        List<Entity> candidateEntities = level.getEntities((Entity) null, scanBox, e -> {
            if (e.isSpectator()) return false;
            if (e instanceof Player p) {
                return p.isFallFlying() || p.getAbilities().flying || p.position().y > pos.getY() + 8;
            }
            if (e instanceof Projectile) return true;
            if (e instanceof Phantom) return true;
            // Check for airship or vehicle entities
            return !e.onGround() && e.position().y > pos.getY() + 2 && e.getDeltaMovement().lengthSqr() > 0.01;
        });

        int previousCount = radar.contactCount;
        radar.contactCount = candidateEntities.size();

        if (radar.contactCount > 0) {
            double minDist = Double.MAX_VALUE;
            Entity closest = null;
            Vec3 center = Vec3.atCenterOf(pos);
            for (Entity entity : candidateEntities) {
                double dist = entity.position().distanceTo(center);
                if (dist < minDist) {
                    minDist = dist;
                    closest = entity;
                }
            }
            radar.nearestDistance = minDist;
            if (closest != null) {
                radar.nearestInfo = closest.getType().getDescription().getString() + " (Y=" + (int) closest.getY() + ")";
            }

            if (!state.getValue(AirspaceRadarBlock.LIT)) {
                level.setBlock(pos, state.setValue(AirspaceRadarBlock.LIT, true), 3);
                level.playSound(null, pos, ModSounds.RADAR_ALERT.get(), SoundSource.BLOCKS, 1.0f, 1.0f);
            } else if (radar.tickCount % 60 == 0) {
                level.playSound(null, pos, ModSounds.RADAR_PING.get(), SoundSource.BLOCKS, 0.7f, 1.2f);
            }
        } else {
            radar.nearestDistance = 0.0;
            radar.nearestInfo = "None";
            if (state.getValue(AirspaceRadarBlock.LIT)) {
                level.setBlock(pos, state.setValue(AirspaceRadarBlock.LIT, false), 3);
            }
        }

        if (radar.contactCount != previousCount) {
            radar.setChanged();
            level.updateNeighbourForOutputSignal(pos, state.getBlock());
        }
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.putInt("Contacts", contactCount);
        tag.putDouble("NearestDist", nearestDistance);
        tag.putString("NearestInfo", nearestInfo);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        contactCount = tag.getInt("Contacts");
        nearestDistance = tag.getDouble("NearestDist");
        nearestInfo = tag.getString("NearestInfo");
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
