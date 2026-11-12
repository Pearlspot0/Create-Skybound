package com.create_skybound.blockentity;

import com.create_skybound.block.BallastVentBlock;
import com.create_skybound.registry.ModBlockEntities;
import com.create_skybound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.List;

public class BallastVentBlockEntity extends BlockEntity {
    private int tickCount = 0;

    public BallastVentBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.BALLAST_VENT.get(), pos, state);
    }

    public static void tick(Level level, BlockPos pos, BlockState state, BallastVentBlockEntity vent) {
        vent.tickCount++;
        boolean powered = state.getValue(BallastVentBlock.POWERED);
        if (!powered) return;

        Direction dir = state.getValue(BallastVentBlock.FACING);
        Vec3 ventDir = Vec3.atLowerCornerOf(dir.getNormal());

        if (level.isClientSide) {
            Vec3 center = Vec3.atCenterOf(pos).add(ventDir.scale(0.55));
            for (int i = 0; i < 3; i++) {
                double speed = 0.3 + level.random.nextDouble() * 0.2;
                level.addParticle(ParticleTypes.CLOUD,
                        center.x + (level.random.nextDouble() - 0.5) * 0.3,
                        center.y + (level.random.nextDouble() - 0.5) * 0.3,
                        center.z + (level.random.nextDouble() - 0.5) * 0.3,
                        ventDir.x * speed, ventDir.y * speed, ventDir.z * speed);
            }
        } else {
            if (vent.tickCount % 20 == 0) {
                level.playSound(null, pos, ModSounds.BALLAST_VENT.get(), SoundSource.BLOCKS, 0.7f, 1.2f);
            }

            // Push entities in the exhaust jet
            BlockPos startPos = pos.relative(dir);
            BlockPos endPos = pos.relative(dir, 5);
            AABB jetBox = new AABB(startPos).minmax(new AABB(endPos)).inflate(0.5);

            List<Entity> affected = level.getEntities((Entity) null, jetBox, e -> !e.isSpectator());
            for (Entity entity : affected) {
                Vec3 current = entity.getDeltaMovement();
                double pushForce = 0.22;
                entity.setDeltaMovement(current.add(ventDir.scale(pushForce)));
                if (dir == Direction.UP) {
                    entity.resetFallDistance();
                }
                entity.hurtMarked = true;
            }
        }
    }
}
