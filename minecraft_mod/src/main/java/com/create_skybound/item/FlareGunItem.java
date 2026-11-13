package com.create_skybound.item;

import com.create_skybound.entity.SignalFlareEntity;
import com.create_skybound.registry.ModItems;
import com.create_skybound.registry.ModSounds;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

public class FlareGunItem extends Item {
    public FlareGunItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);

        ItemStack ammoStack = findAmmo(player);
        boolean creative = player.getAbilities().instabuild;

        if (ammoStack.isEmpty() && !creative) {
            return InteractionResultHolder.fail(held);
        }

        if (!level.isClientSide) {
            int rgb = 0xFF3322; // Crimson
            if (!ammoStack.isEmpty() && ammoStack.getItem() instanceof SignalFlareItem flareItem) {
                rgb = flareItem.getColorRgb();
            }

            SignalFlareEntity flare = new SignalFlareEntity(level, player, rgb);
            flare.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 1.8F, 1.0F);
            level.addFreshEntity(flare);

            if (!creative && !ammoStack.isEmpty()) {
                ammoStack.shrink(1);
            }

            EquipmentSlot slot = (hand == InteractionHand.MAIN_HAND) ? EquipmentSlot.MAINHAND : EquipmentSlot.OFFHAND;
            held.hurtAndBreak(1, player, slot);
        }

        level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.FLARE_FIRE.get(), SoundSource.PLAYERS, 1.0F, 1.0F);
        player.getCooldowns().addCooldown(this, 25);
        player.awardStat(Stats.ITEM_USED.get(this));

        return InteractionResultHolder.sidedSuccess(held, level.isClientSide);
    }

    private ItemStack findAmmo(Player player) {
        if (player.getOffhandItem().is(ModItems.SIGNAL_FLARE.get())) {
            return player.getOffhandItem();
        }
        for (ItemStack item : player.getInventory().items) {
            if (item.is(ModItems.SIGNAL_FLARE.get())) {
                return item;
            }
        }
        return ItemStack.EMPTY;
    }
}
