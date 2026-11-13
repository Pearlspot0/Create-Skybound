package com.create_skybound.blockentity;

import com.create_skybound.block.MooringWinchBlock;
import com.create_skybound.registry.ModBlockEntities;
import com.create_skybound.registry.ModItems;
import com.create_skybound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Containers;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class MooringWinchBlockEntity extends BlockEntity {
    @Nullable
    private BlockPos linkedPos = null;
    private int tickCount = 0;

    public MooringWinchBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.MOORING_WINCH.get(), pos, state);
    }

    public boolean isTethered() {
        return linkedPos != null;
    }

    @Nullable
    public BlockPos getLinkedPos() {
        return linkedPos;
    }

    public void setLinkedPos(@Nullable BlockPos pos) {
        this.linkedPos = pos;
        if (level != null && !level.isClientSide) {
            boolean hasTether = (linkedPos != null);
            if (getBlockState().getValue(MooringWinchBlock.TETHERED) != hasTether) {
                level.setBlock(getBlockPos(), getBlockState().setValue(MooringWinchBlock.TETHERED, hasTether), 3);
            }
            setChanged();
            level.sendBlockUpdated(getBlockPos(), getBlockState(), getBlockState(), 3);
        }
    }

    public void untether(boolean dropItem) {
        if (dropItem && level != null && !level.isClientSide && isTethered()) {
            Containers.dropItemStack(level, getBlockPos().getX() + 0.5, getBlockPos().getY() + 0.5, getBlockPos().getZ() + 0.5, new ItemStack(ModItems.MOORING_CABLE.get()));
        }
        if (linkedPos != null && level != null) {
            BlockPos other = linkedPos;
            this.linkedPos = null;
            if (level.getBlockEntity(other) instanceof MooringCleatBlockEntity otherCleat) {
                if (getBlockPos().equals(otherCleat.getLinkedPos())) {
                    otherCleat.setLinkedPos(null);
                }
            }
        }
        setLinkedPos(null);
    }

    public static void tick(Level level, BlockPos pos, BlockState state, MooringWinchBlockEntity winch) {
        winch.tickCount++;
        if (winch.linkedPos == null) return;

        double distSq = pos.distSqr(winch.linkedPos);
        if (distSq > 48 * 48) {
            winch.untether(true);
            return;
        }

        boolean powered = state.getValue(MooringWinchBlock.POWERED);

        if (!level.isClientSide && powered && winch.tickCount % 2 == 0) {
            Vec3 targetCenter = Vec3.atCenterOf(winch.linkedPos);
            Vec3 winchCenter = Vec3.atCenterOf(pos);
            Vec3 pullDir = winchCenter.subtract(targetCenter).normalize().scale(0.12);

            // Pull entities near the tethered location towards the winch
            AABB area = new AABB(winch.linkedPos).inflate(3.5);
            List<Entity> entities = level.getEntities((Entity) null, area, e -> !e.isSpectator());
            for (Entity entity : entities) {
                Vec3 currentDelta = entity.getDeltaMovement();
                entity.setDeltaMovement(currentDelta.add(pullDir.x, pullDir.y * 0.5, pullDir.z));
                entity.hurtMarked = true;
            }

            if (winch.tickCount % 20 == 0) {
                level.playSound(null, pos, ModSounds.WINCH_WIND.get(), SoundSource.BLOCKS, 0.8f, 1.0f);
            }
        }

        // Particle rendering for the cable
        if (level.isClientSide && winch.tickCount % 4 == 0) {
            spawnCableParticles(level, pos, winch.linkedPos);
        }
    }

    private static void spawnCableParticles(Level level, BlockPos from, BlockPos to) {
        Vec3 start = Vec3.atCenterOf(from);
        Vec3 end = Vec3.atCenterOf(to);
        Vec3 dir = end.subtract(start);
        double len = dir.length();
        if (len <= 0.01) return;

        int steps = Math.max(3, (int) (len * 2));
        for (int i = 0; i <= steps; i++) {
            double progress = (double) i / steps;
            double sag = Math.sin(progress * Math.PI) * 0.2;
            Vec3 point = start.add(dir.scale(progress)).subtract(0, sag, 0);
            level.addParticle(ParticleTypes.CRIT, point.x, point.y, point.z, 0, -0.01, 0);
        }
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        if (linkedPos != null) {
            tag.put("LinkedPos", NbtUtils.writeBlockPos(linkedPos));
        }
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        if (tag.contains("LinkedPos")) {
            NbtUtils.readBlockPos(tag, "LinkedPos").ifPresent(pos -> this.linkedPos = pos);
        } else {
            this.linkedPos = null;
        }
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
