package com.create_skybound.compat;

import com.create_skybound.CreateSkybound;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;

@EventBusSubscriber(modid = CreateSkybound.MODID, bus = EventBusSubscriber.Bus.GAME)
public class WrenchHandler {

    @SubscribeEvent
    public static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        Level level = event.getLevel();
        BlockPos pos = event.getPos();
        BlockState state = level.getBlockState(pos);
        Player player = event.getEntity();
        ItemStack held = event.getItemStack();

        String namespace = state.getBlock().asItem().toString();
        boolean isSkyboundBlock = namespace.contains("create_skybound");

        if (!isSkyboundBlock) return;
        if (!CreateCompat.isWrench(held)) return;

        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.SUCCESS);

        if (level.isClientSide) {
            player.swing(event.getHand());
            return;
        }

        if (player.isShiftKeyDown()) {
            level.destroyBlock(pos, true, player);
            level.playSound(null, pos, SoundEvents.ARMOR_EQUIP_IRON.value(), SoundSource.BLOCKS, 1.0f, 1.2f);
        } else {
            BlockState rotated = CreateCompat.rotateBlock(state);
            if (!rotated.equals(state)) {
                level.setBlock(pos, rotated, 3);
                level.playSound(null, pos, SoundEvents.SPYGLASS_USE, SoundSource.BLOCKS, 1.0f, 1.3f);
            }
        }

        player.swing(event.getHand());
    }
}
