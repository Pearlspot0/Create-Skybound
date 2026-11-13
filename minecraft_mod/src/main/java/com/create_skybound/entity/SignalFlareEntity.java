package com.create_skybound.entity;

import com.create_skybound.registry.ModEntities;
import com.create_skybound.registry.ModItems;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

public class SignalFlareEntity extends ThrowableItemProjectile {
    private static final EntityDataAccessor<Integer> COLOR_RGB =
            SynchedEntityData.defineId(SignalFlareEntity.class, EntityDataSerializers.INT);

    private int age = 0;
    private boolean parachuteDeployed = false;

    public SignalFlareEntity(EntityType<? extends ThrowableItemProjectile> type, Level level) {
        super(type, level);
    }

    public SignalFlareEntity(Level level, LivingEntity shooter, int rgb) {
        super(ModEntities.SIGNAL_FLARE.get(), shooter, level);
        this.entityData.set(COLOR_RGB, rgb);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(COLOR_RGB, 0xFF4422); // Default brilliant crimson red
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.SIGNAL_FLARE.get();
    }

    public int getColorRgb() {
        return this.entityData.get(COLOR_RGB);
    }

    @Override
    public void tick() {
        super.tick();
        this.age++;

        Vec3 motion = this.getDeltaMovement();

        // After reaching apex or falling, deploy parachute
        if (this.age > 15 && motion.y < 0.0) {
            this.parachuteDeployed = true;
            // Gentle parachute descent
            this.setDeltaMovement(motion.x * 0.95, Math.max(motion.y * 0.8, -0.06), motion.z * 0.95);
        }

        Level level = this.level();
        if (level.isClientSide) {
            int rgb = getColorRgb();
            float r = ((rgb >> 16) & 0xFF) / 255.0f;
            float g = ((rgb >> 8) & 0xFF) / 255.0f;
            float b = (rgb & 0xFF) / 255.0f;

            DustParticleOptions dust = new DustParticleOptions(new Vector3f(r, g, b), 2.0f);
            level.addParticle(dust, this.getX(), this.getY(), this.getZ(), 0, -0.02, 0);
            level.addParticle(ParticleTypes.FLAME, this.getX(), this.getY(), this.getZ(), 0, 0, 0);

            if (this.parachuteDeployed && this.age % 3 == 0) {
                level.addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE, this.getX(), this.getY() + 0.3, this.getZ(), 0, 0.02, 0);
            }
        }

        // Expire after 30 seconds
        if (this.age > 600) {
            this.discard();
        }
    }

    @Override
    protected void onHit(HitResult result) {
        super.onHit(result);
        if (!this.level().isClientSide && !this.parachuteDeployed) {
            this.parachuteDeployed = true;
        }
    }

    @Override
    public void addAdditionalSaveData(CompoundTag compound) {
        super.addAdditionalSaveData(compound);
        compound.putInt("FlareAge", this.age);
        compound.putInt("ColorRgb", getColorRgb());
        compound.putBoolean("Parachute", this.parachuteDeployed);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag compound) {
        super.readAdditionalSaveData(compound);
        this.age = compound.getInt("FlareAge");
        if (compound.contains("ColorRgb")) {
            this.entityData.set(COLOR_RGB, compound.getInt("ColorRgb"));
        }
        this.parachuteDeployed = compound.getBoolean("Parachute");
    }
}
