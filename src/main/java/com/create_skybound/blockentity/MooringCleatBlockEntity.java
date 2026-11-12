package com.create_skybound.blockentity;

import com.create_skybound.block.MooringCleatBlock;
import com.create_skybound.registry.ModBlockEntities;
import com.create_skybound.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.Containers;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

public class MooringCleatBlockEntity extends BlockEntity {
    @Nullable
    private BlockPos linkedPos = null;
    private int tickCount = 0;

    public MooringCleatBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.MOORING_CLEAT.get(), pos, state);
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
            if (getBlockState().getValue(MooringCleatBlock.TETHERED) != hasTether) {
                level.setBlock(getBlockPos(), getBlockState().setValue(MooringCleatBlock.TETHERED, hasTether), 3);
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
            } else if (level.getBlockEntity(other) instanceof MooringWinchBlockEntity otherWinch) {
                if (getBlockPos().equals(otherWinch.getLinkedPos())) {
                    otherWinch.setLinkedPos(null);
                }
            }
        }
        setLinkedPos(null);
    }

    public static void tick(Level level, BlockPos pos, BlockState state, MooringCleatBlockEntity cleat) {
        cleat.tickCount++;
        if (cleat.linkedPos == null) return;

        // Verify connection distance (max 48 blocks)
        double distSq = pos.distSqr(cleat.linkedPos);
        if (distSq > 48 * 48) {
            cleat.untether(true);
            return;
        }

        // Render particle cable line occasionally on client
        if (level.isClientSide && cleat.tickCount % 4 == 0) {
            spawnCableParticles(level, pos, cleat.linkedPos);
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
            // Add a slight catenary droop to the cable
            double sag = Math.sin(progress * Math.PI) * 0.25;
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
