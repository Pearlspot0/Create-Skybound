package com.create_skybound.block;

import com.create_skybound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

public class AirshipBumperBlock extends Block {
    public AirshipBumperBlock(Properties properties) {
        super(properties);
    }

    @Override
    public void fallOn(Level level, BlockState state, BlockPos pos, Entity entity, float fallDistance) {
        // Completely absorb fall damage
        entity.causeFallDamage(fallDistance, 0.0f, level.damageSources().fall());
    }

    @Override
    public void updateEntityAfterFallOn(BlockGetter level, Entity entity) {
        if (entity.isSuppressingBounce()) {
            super.updateEntityAfterFallOn(level, entity);
        } else {
            this.bounceEntity(entity);
        }
    }

    private void bounceEntity(Entity entity) {
        Vec3 delta = entity.getDeltaMovement();
        if (delta.y < 0.0) {
            double bounceSpeed = entity instanceof net.minecraft.world.entity.LivingEntity ? 0.75 : 0.6;
            entity.setDeltaMovement(delta.x, -delta.y * bounceSpeed, delta.z);
            entity.resetFallDistance();

            Level level = entity.level();
            if (!level.isClientSide) {
                level.playSound(null, entity.blockPosition(), ModSounds.BUMPER_IMPACT.get(), SoundSource.BLOCKS, 0.8f, 1.2f);
            } else {
                for (int i = 0; i < 5; i++) {
                    level.addParticle(ParticleTypes.CLOUD, entity.getX(), entity.getY(), entity.getZ(),
                            (level.random.nextDouble() - 0.5) * 0.2, 0.1, (level.random.nextDouble() - 0.5) * 0.2);
                }
            }
        }
    }

    @Override
    public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        double deltaLen = entity.getDeltaMovement().length();
        if (deltaLen > 0.4) {
            if (level.isClientSide) {
                level.addParticle(ParticleTypes.CLOUD, entity.getX(), entity.getY() + 0.1, entity.getZ(), 0, 0.05, 0);
            }
        }
        super.stepOn(level, pos, state, entity);
    }
}
