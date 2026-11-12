package com.create_skybound.item;

import com.create_skybound.entity.SignalFlareEntity;
import com.create_skybound.registry.ModSounds;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

public class SignalFlareItem extends Item {
    private final int colorRgb;

    public SignalFlareItem(Properties properties, int colorRgb) {
        super(properties);
        this.colorRgb = colorRgb;
    }

    public int getColorRgb() {
        return colorRgb;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);

        level.playSound(null, player.getX(), player.getY(), player.getZ(),
                ModSounds.FLARE_FIRE.get(), SoundSource.PLAYERS, 0.6F, 1.3F);

        if (!level.isClientSide) {
            SignalFlareEntity flare = new SignalFlareEntity(level, player, colorRgb);
            flare.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 1.2F, 1.0F);
            level.addFreshEntity(flare);

            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
            }
        }

        player.awardStat(Stats.ITEM_USED.get(this));
        player.getCooldowns().addCooldown(this, 15);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }
}
