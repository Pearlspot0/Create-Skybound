package com.create_skybound.item;

import com.create_skybound.blockentity.SkywayBeaconBlockEntity;
import com.create_skybound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

public class FlightSextantItem extends Item {
    public FlightSextantItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);

        if (!level.isClientSide) {
            Vec3 playerPos = player.position();
            SkywayBeaconBlockEntity beacon = SkywayBeaconBlockEntity.findNearest(level, playerPos);

            if (beacon != null) {
                BlockPos bPos = beacon.getBlockPos();
                double dx = bPos.getX() + 0.5 - playerPos.x;
                double dz = bPos.getZ() + 0.5 - playerPos.z;
                int dy = bPos.getY() - (int) playerPos.y;

                double distance = Math.sqrt(dx * dx + dz * dz + (double) (dy * dy));
                double angleDeg = Math.toDegrees(Math.atan2(-dx, dz));
                if (angleDeg < 0) angleDeg += 360;

                String cardinal = getCardinal(angleDeg);
                String yStr = (dy >= 0 ? "+" : "") + dy + "m";

                player.displayClientMessage(Component.translatable("message.create_skybound.sextant_reading",
                        (int) distance, String.format("%03d", (int) angleDeg), cardinal, yStr), true);
                level.playSound(null, player.blockPosition(), ModSounds.BEACON_PULSE.get(), SoundSource.PLAYERS, 0.6f, 1.4f);
            } else {
                player.displayClientMessage(Component.translatable("message.create_skybound.sextant_none"), true);
            }
        }

        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    private static String getCardinal(double deg) {
        String[] directions = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
        int index = (int) Math.round(((deg % 360) / 45)) % 8;
        return directions[index];
    }
}
