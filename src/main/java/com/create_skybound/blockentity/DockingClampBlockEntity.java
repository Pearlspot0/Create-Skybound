package com.create_skybound.blockentity;

import com.create_skybound.block.DockingClampBlock;
import com.create_skybound.registry.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class DockingClampBlockEntity extends BlockEntity {
    private boolean dockedVessel = false;
    private int tickCount = 0;

    public DockingClampBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.DOCKING_CLAMP.get(), pos, state);
    }

    public boolean hasDockedVessel() {
        return dockedVessel;
    }

    public static void tick(Level level, BlockPos pos, BlockState state, DockingClampBlockEntity clamp) {
        clamp.tickCount++;
        boolean locked = state.getValue(DockingClampBlock.LOCKED);
        if (!locked) {
            if (clamp.dockedVessel) {
                clamp.dockedVessel = false;
                if (!level.isClientSide) {
                    clamp.setChanged();
                    level.updateNeighbourForOutputSignal(pos, state.getBlock());
                }
            }
            return;
        }

        Direction facing = state.getValue(DockingClampBlock.FACING);
        BlockPos clampZone = pos.relative(facing);
        AABB captureBox = new AABB(clampZone).inflate(1.2);

        List<Entity> vessels = level.getEntities((Entity) null, captureBox, e -> !(e instanceof Player));
        boolean foundVessel = !vessels.isEmpty();

        if (foundVessel) {
            Vec3 lockPoint = Vec3.atCenterOf(clampZone);
            for (Entity entity : vessels) {
                // Dampen velocity to lock in place
                entity.setDeltaMovement(Vec3.ZERO);
                // Gently snap toward center of docking area
                Vec3 current = entity.position();
                Vec3 correction = lockPoint.subtract(current).scale(0.1);
                entity.setPos(current.add(correction.x, correction.y, correction.z));
                entity.resetFallDistance();
                entity.hurtMarked = true;
            }
        }

        if (clamp.dockedVessel != foundVessel) {
            clamp.dockedVessel = foundVessel;
            if (!level.isClientSide) {
                clamp.setChanged();
                level.updateNeighbourForOutputSignal(pos, state.getBlock());
            }
        }

        if (level.isClientSide && clamp.dockedVessel && clamp.tickCount % 6 == 0) {
            Vec3 sparkPos = Vec3.atCenterOf(pos).add(Vec3.atLowerCornerOf(facing.getNormal()).scale(0.6));
            level.addParticle(ParticleTypes.ELECTRIC_SPARK, sparkPos.x, sparkPos.y, sparkPos.z, 0, 0.05, 0);
        }
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.putBoolean("DockedVessel", dockedVessel);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        dockedVessel = tag.getBoolean("DockedVessel");
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
